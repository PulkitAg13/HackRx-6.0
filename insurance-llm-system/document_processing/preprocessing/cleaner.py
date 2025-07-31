import logging
import re
from typing import Optional
from ...backend.app.core.config import settings

logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self):
        self.replace_patterns = [
            (r'\s+', ' '),  # Multiple whitespace to single
            (r'-\n', ''),    # Hyphenated line breaks
            (r'\n', ' '),    # Newlines to space
            (r'\t', ' '),    # Tabs to space
            (r'\x0c', ' '),  # Form feed to space
        ]
        
        if settings.CLEANER_CONFIG.get("remove_special_chars", True):
            self.replace_patterns.append((r'[^\w\s-]', ''))  # Remove special chars
        
        self.stop_words = set(settings.CLEANER_CONFIG.get("stop_words", []))

    def clean_text(self, text: str) -> Optional[str]:
        """Clean and normalize text"""
        if not text:
            return None
            
        try:
            # Apply replacement patterns
            for pattern, repl in self.replace_patterns:
                text = re.sub(pattern, repl, text)
            
            # Case normalization
            if settings.CLEANER_CONFIG.get("lowercase", True):
                text = text.lower()
            
            # Remove stopwords if enabled
            if settings.CLEANER_CONFIG.get("remove_stopwords", False):
                words = text.split()
                words = [w for w in words if w not in self.stop_words]
                text = " ".join(words)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Text cleaning failed: {str(e)}")
            raise

def clean_text(text: str) -> Optional[str]:
    return TextCleaner().clean_text(text)