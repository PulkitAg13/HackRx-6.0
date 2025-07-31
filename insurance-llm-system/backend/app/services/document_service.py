import os
import logging
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import crud
from ..core.config import settings
from ....document_processing.text_extraction import extract_text
from ....document_processing.preprocessing import clean_text, chunk_text
from ....document_processing.vector_db import initialize_vector_db, store_clauses
from ....ml_models.embedding_models.ada_embeddings import get_embeddings

logger = logging.getLogger(__name__)

async def initialize_document_service():
    """Initialize document processing services"""
    try:
        await initialize_vector_db()
        logger.info("Document service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize document service: {str(e)}")
        raise

async def process_uploaded_document(db: Session, file) -> dict:
    """Process an uploaded document through the full pipeline"""
    try:
        # Validate file
        validate_file(file)
        
        # Save file metadata to database
        document = save_document_metadata(db, file)
        
        # Extract text from document
        text = extract_text(file.file, file.filename)
        
        # Clean and chunk text
        cleaned_text = clean_text(text)
        chunks = chunk_text(cleaned_text)
        
        # Process each chunk (section/clause)
        clauses = []
        for i, chunk in enumerate(chunks):
            clause = process_text_chunk(db, document.id, chunk, i)
            clauses.append(clause)
        
        # Update document as processed
        update_document_processed(db, document.id)
        
        return document
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
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {file_ext}")

def save_document_metadata(db: Session, file) -> dict:
    """Save document metadata to database"""
    file_ext = file.filename.split('.')[-1].lower()
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

def process_text_chunk(db: Session, document_id: int, text: str, chunk_index: int) -> dict:
    """Process a single text chunk into a clause"""
    # Get embeddings for the chunk
    embeddings = get_embeddings(text)
    
    # Create clause in database
    clause = crud.create_clause(
        db,
        document_id=document_id,
        clause_text=text,
        section=f"Section {chunk_index + 1}"
    )
    
    # Store embeddings in vector DB
    store_clauses([{
        "id": clause.id,
        "text": text,
        "embeddings": embeddings,
        "document_id": document_id
    }])
    
    return clause

def update_document_processed(db: Session, document_id: int):
    """Mark document as processed in database"""
    document = crud.get_document(db, document_id)
    if document:
        document.processed = True
        db.commit()
        db.refresh(document)