import logging
from typing import List, Dict, Optional, Union
from pinecone import Pinecone, ServerlessSpec
from backend.app.core.config import settings
from ml_models.embedding_models.ada_embeddings import get_embeddings

logger = logging.getLogger(__name__)

class PineconeManager:
    def __init__(self):
        """Initialize Pinecone connection and index with comprehensive error handling"""
        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone API key is missing in settings")
        if not settings.PINECONE_INDEX_NAME:
            raise ValueError("Pinecone index name is missing in settings")

        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Check if index exists or create it
            if settings.PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
                logger.info(f"Creating new index: {settings.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # Update with your embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-west-2"
                    )
                )
            
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info(f"Successfully connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")
            
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {str(e)}")
            logger.error("Please verify:")
            logger.error("1. Your API key is correct and has proper permissions")
            logger.error("2. Your index name follows Pinecone naming conventions")
            logger.error("3. Your account has available resources")
            raise

    def upsert_clauses(self, clauses: List[Dict]) -> bool:
        """Store document clauses in Pinecone with embeddings"""
        try:
            vectors = []
            for clause in clauses:
                if not isinstance(clause, dict) or "text" not in clause:
                    logger.warning(f"Skipping invalid clause: {clause}")
                    continue
                    
                embedding = get_embeddings(clause["text"])
                vectors.append({
                    "id": str(clause.get("id", "")),
                    "values": embedding,
                    "metadata": {
                        "document_id": clause.get("document_id", ""),
                        "text": clause["text"],
                        "section": clause.get("section", ""),
                        "page_number": clause.get("page_number", 0)
                    }
                })
            
            if vectors:
                self.index.upsert(vectors=vectors)
                logger.info(f"Upserted {len(vectors)} clauses to Pinecone")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Pinecone upsert operation failed: {str(e)}")
            raise

    def search_clauses(self, query_embedding: List[float], document_id: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """Search for relevant clauses with optional document filtering"""
        try:
            query_filter = {"document_id": document_id} if document_id else None
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=query_filter,
                include_metadata=True
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata["text"],
                    "section": match.metadata.get("section", ""),
                    "page_number": match.metadata.get("page_number", 0)
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Pinecone search failed: {str(e)}")
            raise

    def delete_clauses(self, document_id: str) -> bool:
        """Delete all clauses for a specific document"""
        try:
            self.index.delete(filter={"document_id": document_id})
            logger.info(f"Deleted clauses for document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Pinecone deletion failed: {str(e)}")
            raise

# Global Pinecone manager instance
pinecone_manager: Union[PineconeManager, None] = None

def initialize_pinecone() -> PineconeManager:
    """Initialize and return Pinecone manager instance"""
    global pinecone_manager
    if pinecone_manager is None:
        pinecone_manager = PineconeManager()
    return pinecone_manager

def get_vector_store() -> PineconeManager:
    """Get the Pinecone vector store instance with lazy initialization"""
    global pinecone_manager
    if pinecone_manager is None:
        pinecone_manager = PineconeManager()
    return pinecone_manager

def search_clauses(query_embedding: List[float], document_id: Optional[str] = None, top_k: int = 5) -> List[Dict]:
    """Standalone search function for backward compatibility"""
    return get_vector_store().search_clauses(query_embedding, document_id, top_k)

def upsert_clauses(clauses: List[Dict]) -> bool:
    """Standalone upsert function for backward compatibility"""
    return get_vector_store().upsert_clauses(clauses)

def delete_clauses(document_id: str) -> bool:
    """Standalone delete function"""
    return get_vector_store().delete_clauses(document_id)