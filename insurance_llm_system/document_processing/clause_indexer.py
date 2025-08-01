import logging
from typing import Dict, List
from .text_extraction import parse_pdf, parse_docx, parse_email
from .preprocessing import clean_text, chunk_text, detect_sections
from .vector_db import get_embedding_store
from ... import settings

logger = logging.getLogger(__name__)

class ClauseIndexer:
    def __init__(self):
        self.embedding_store = get_embedding_store()

    def process_document(self, file_stream, file_type: str) -> Dict:
        """Process document and index its clauses"""
        try:
            # Parse document based on type
            if file_type == "pdf":
                parsed = parse_pdf(file_stream)
            elif file_type == "docx":
                parsed = parse_docx(file_stream)
            elif file_type == "email":
                parsed = parse_email(file_stream)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Clean and preprocess text
            cleaned_text = clean_text(parsed["text"])
            sections = detect_sections(cleaned_text)
            
            # Extract clauses from sections
            clauses = []
            for section_type, section_data in sections.items():
                for section in section_data:
                    chunks = chunk_text(section["text"])
                    for i, chunk in enumerate(chunks):
                        clauses.append({
                            "text": chunk,
                            "section": f"{section_type}_{i}",
                            "metadata": {
                                "document_title": parsed.get("metadata", {}).get("title", ""),
                                "section_title": section["title"]
                            }
                        })
            
            return {
                "document_metadata": parsed.get("metadata", {}),
                "clauses": clauses
            }
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            raise

    def index_clauses(self, document_id: str, clauses: List[Dict]) -> bool:
        """Index clauses in vector database"""
        try:
            # Prepare clauses for indexing
            indexed_clauses = []
            for i, clause in enumerate(clauses):
                indexed_clauses.append({
                    "id": f"{document_id}_{i}",
                    "document_id": document_id,
                    "text": clause["text"],
                    "section": clause.get("section", "")
                })
            
            # Store in vector DB
            return self.embedding_store.store_clauses(indexed_clauses)
        except Exception as e:
            logger.error(f"Clause indexing failed: {str(e)}")
            raise

def index_document(file_stream, file_type: str, document_id: str) -> Dict:
    """Full document indexing pipeline"""
    try:
        indexer = ClauseIndexer()
        processed = indexer.process_document(file_stream, file_type)
        success = indexer.index_clauses(document_id, processed["clauses"])
        return {
            "success": success,
            "document_metadata": processed["document_metadata"],
            "clause_count": len(processed["clauses"])
        }
    except Exception as e:
        logger.error(f"Document indexing failed: {str(e)}")
        raise