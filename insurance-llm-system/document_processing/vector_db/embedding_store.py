import logging
from typing import List, Dict, Optional
from ...backend.config import settings
from .pinecone_integration import initialize_pinecone
from .chroma_integration import initialize_chroma

logger = logging.getLogger(__name__)

class EmbeddingStore:
    def __init__(self):
        self.db = None
        if settings.VECTOR_DB == "pinecone":
            self.db = initialize_pinecone()
        elif settings.VECTOR_DB == "chroma":
            self.db = initialize_chroma()
        else:
            raise ValueError(f"Unsupported vector DB: {settings.VECTOR_DB}")

    def store_clauses(self, clauses: List[Dict]) -> bool:
        """Store clauses in configured vector DB"""
        if not self.db:
            raise ValueError("Vector DB not initialized")
        return self.db.upsert_clauses(clauses)

    def search_clauses(self, query_embedding: List[float], document_id: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant clauses"""
        if not self.db:
            raise ValueError("Vector DB not initialized")
        return self.db.search_clauses(query_embedding, document_id, top_k)

def get_embedding_store():
    """Get initialized embedding store instance"""
    try:
        return EmbeddingStore()
    except Exception as e:
        logger.error(f"Embedding store initialization failed: {str(e)}")
        raise