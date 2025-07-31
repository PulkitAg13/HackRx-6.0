import logging
from typing import List
from ...backend.config import settings

logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        try:
            if len(text) <= self.chunk_size:
                return [text]
            
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunk = text[start:end]
                chunks.append(chunk)
                start = end - self.chunk_overlap
                
                # Prevent infinite loop with small overlap
                if start <= 0:
                    start = end
                    
            return chunks
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            raise

def chunk_text(text: str) -> List[str]:
    return TextChunker().chunk_text(text)