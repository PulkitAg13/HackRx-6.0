import logging
import chromadb
from typing import List, Dict
from backend.app.core.config import settings
from ml_models.embedding_models.ada_embeddings import get_embeddings

logger = logging.getLogger(__name__)

class ChromaManager:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )

    def upsert_clauses(self, clauses: List[Dict]) -> bool:
        """Store clauses in ChromaDB"""
        try:
            ids = [str(c["id"]) for c in clauses]
            embeddings = [get_embeddings(c["text"]) for c in clauses]
            metadatas = [{
                "document_id": c["document_id"],
                "text": c["text"],
                "section": c.get("section", "")
            } for c in clauses]
            
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            logger.error(f"ChromaDB upsert failed: {str(e)}")
            raise

    def search_clauses(self, query_embedding: List[float], document_id: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant clauses"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"document_id": document_id}
            )
            
            return [
                {
                    "id": results["ids"][0][i],
                    "score": results["distances"][0][i],
                    "text": results["metadatas"][0][i]["text"],
                    "section": results["metadatas"][0][i]["section"]
                }
                for i in range(len(results["ids"][0]))
            ]
        except Exception as e:
            logger.error(f"ChromaDB search failed: {str(e)}")
            raise

def initialize_chroma():
    """Initialize ChromaDB connection"""
    try:
        return ChromaManager()
    except Exception as e:
        logger.error(f"ChromaDB initialization failed: {str(e)}")
        raise