import logging
import pinecone
from typing import List, Dict, Optional
from backend.app.core.config import settings
from insurance_llm_system.ml_models.embedding_models import get_embeddings

logger = logging.getLogger(__name__)

class PineconeManager:
    def __init__(self):
        if not all([settings.PINECONE_API_KEY, settings.PINECONE_ENVIRONMENT, settings.PINECONE_INDEX_NAME]):
            raise ValueError("Pinecone configuration missing")
        
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)

    def upsert_clauses(self, clauses: List[Dict]) -> bool:
        """Store clauses in Pinecone with embeddings"""
        try:
            vectors = []
            for clause in clauses:
                embedding = get_embeddings(clause["text"])
                vectors.append({
                    "id": str(clause["id"]),
                    "values": embedding,
                    "metadata": {
                        "document_id": clause["document_id"],
                        "text": clause["text"],
                        "section": clause.get("section", "")
                    }
                })
            
            self.index.upsert(vectors=vectors)
            return True
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {str(e)}")
            raise

    def search_clauses(self, query_embedding: List[float], document_id: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant clauses"""
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter={"document_id": document_id},
                include_metadata=True
            )
            return [
                {
                    "id": match["id"],
                    "score": match["score"],
                    "text": match["metadata"]["text"],
                    "section": match["metadata"]["section"]
                }
                for match in results["matches"]
            ]
        except Exception as e:
            logger.error(f"Pinecone search failed: {str(e)}")
            raise

def initialize_pinecone():
    """Initialize Pinecone connection"""
    try:
        return PineconeManager()
    except Exception as e:
        logger.error(f"Pinecone initialization failed: {str(e)}")
        raise