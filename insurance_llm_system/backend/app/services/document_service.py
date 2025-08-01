import os
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from io import BytesIO
from ..db import crud
from ..core.config import settings
from document_processing.text_extraction import (
    pdf_parser, docx_parser, email_parser
)
from document_processing.preprocessing import (
    cleaner, chunker, section_detector
)
from ml_models.embedding_models.ada_embeddings import get_embeddings  # or ada_embeddings
from document_processing.vector_db.pinecone_integration import get_vector_store  # or chroma_integration

logger = logging.getLogger(__name__)

vector_store = None

async def initialize_document_service():
    """Initialize document processing services"""
    global vector_store
    try:
        vector_store = get_vector_store()
        logger.info("Document service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize document service: {str(e)}")
        raise

async def process_uploaded_document(db: Session, file) -> Dict:
    """Process an uploaded document through the full pipeline"""
    try:
        # Validate file
        validate_file(file)
        
        # Save file metadata to database
        document = save_document_metadata(db, file)
        
        # Extract text from document
        text = await extract_text_from_file(file)
        
        # Clean and chunk text
        cleaned_text = cleaner(text)
        sections = section_detector(cleaned_text)
        
        # Process each section
        clauses = []
        for section_type, section_data in sections.items():
            for section in section_data:
                section_clauses = process_section(
                    db, document.id, section["text"], section["title"]
                )
                clauses.extend(section_clauses)
        
        # Update document as processed
        update_document_processed(db, document.id)
        
        return {
            "document_id": document.id,
            "filename": document.filename,
            "processed": True,
            "clauses_processed": len(clauses)
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

def validate_file(file):
    """Validate the uploaded file"""
    # Check file size
    max_size = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset pointer
    
    if file_size > max_size:
        raise ValueError(f"File size exceeds maximum of {settings.MAX_DOCUMENT_SIZE_MB}MB")
    
    # Check file type
    file_ext = os.path.splitext(file.filename)[1][1:].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {file_ext}")

async def extract_text_from_file(file):
    """Extract text based on file type"""
    file_ext = os.path.splitext(file.filename)[1][1:].lower()
    file_content = await file.read()
    file_stream = BytesIO(file_content)
    
    if file_ext == "pdf":
        result = pdf_parser(file_stream)
    elif file_ext == "docx":
        result = docx_parser(file_stream)
    elif file_ext in ["eml", "email"]:
        result = email_parser(file_stream)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    return result["text"]

def save_document_metadata(db: Session, file):
    """Save document metadata to database"""
    file_ext = os.path.splitext(file.filename)[1][1:].lower()
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset pointer
    
    document = crud.create_document(
        db,
        filename=file.filename,
        file_type=file_ext,
        file_size=file_size
    )
    return document

def process_section(db: Session, document_id: int, text: str, section_title: str) -> List[Dict]:
    """Process a document section into clauses"""
    chunks = chunker(text)
    clauses = []
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        try:
            # Get embeddings for the chunk
            embeddings = get_embeddings(chunk)
            
            # Create clause in database
            clause = crud.create_clause(
                db,
                document_id=document_id,
                clause_text=chunk,
                section=f"{section_title}_{i+1}",
                embeddings=embeddings
            )
            
            # Store in vector DB
            vector_store.upsert_clauses([{
                "id": clause.id,
                "document_id": document_id,
                "text": chunk,
                "section": f"{section_title}_{i+1}",
                "embeddings": embeddings
            }])
            
            clauses.append({
                "id": clause.id,
                "section": clause.section
            })
        except Exception as e:
            logger.error(f"Error processing section chunk: {str(e)}")
            continue
            
    return clauses

def update_document_processed(db: Session, document_id: int):
    """Mark document as processed in database"""
    document = crud.get_document(db, document_id)
    if document and not document.processed:
        document.processed = True
        db.commit()
        db.refresh(document)