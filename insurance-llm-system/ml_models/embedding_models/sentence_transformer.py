import logging
from sentence_transformers import SentenceTransformer
from ...backend.app.core.config import settings
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)

class SentenceTransformerWrapper:
    def __init__(self):
        try:
            self.model = SentenceTransformer(
                settings.SENTENCE_TRANSFORMER_MODEL,
                cache_folder=settings.MODEL_CACHE_DIR
            )
            logger.info(f"Loaded SentenceTransformer: {settings.SENTENCE_TRANSFORMER_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {str(e)}")
            raise

    def get_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        try:
            if isinstance(texts, str):
                texts = [texts]
            return self.model.encode(texts, convert_to_numpy=True).tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

# Singleton instance
st_wrapper = SentenceTransformerWrapper() if settings.USE_LOCAL_EMBEDDINGS else None

def get_embeddings(texts: Union[str, List[str]]) -> List[List[float]]:
    if not st_wrapper:
        raise ValueError("SentenceTransformer not initialized")
    return st_wrapper.get_embeddings(texts)