import openai
import logging
from typing import List, Union
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIEmbeddings:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = settings.OPENAI_API_KEY

    def get_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            response = openai.Embedding.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            return [item['embedding'] for item in response['data']]
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {str(e)}")
            raise

# Singleton instance
ada_wrapper = OpenAIEmbeddings()

def get_embeddings(texts: Union[str, List[str]]) -> List[List[float]]:
    return ada_wrapper.get_embeddings(texts)