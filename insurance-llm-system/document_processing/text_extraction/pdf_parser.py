import logging
import pdfplumber
from io import BytesIO
from typing import Dict, Optional
from ...backend.app.core.config import settings

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        self.max_pages = settings.PDF_MAX_PAGES

    def extract_text(self, file_stream: BytesIO) -> Dict[str, any]:
        """
        Extract text and metadata from PDF file
        Returns:
            {
                "text": str,
                "metadata": {
                    "page_count": int,
                    "author": str,
                    "title": str,
                    "pages": [
                        {"page_num": int, "text": str}
                    ]
                }
            }
        """
        try:
            with pdfplumber.open(file_stream) as pdf:
                metadata = {
                    "page_count": len(pdf.pages),
                    "author": pdf.metadata.get("Author", ""),
                    "title": pdf.metadata.get("Title", ""),
                    "pages": []
                }
                
                full_text = []
                for i, page in enumerate(pdf.pages[:self.max_pages]):
                    page_text = page.extract_text()
                    metadata["pages"].append({
                        "page_num": i + 1,
                        "text": page_text
                    })
                    full_text.append(page_text)
                
                return {
                    "text": "\n".join(full_text),
                    "metadata": metadata
                }
        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}")
            raise

def parse_pdf(file_stream: BytesIO) -> Dict[str, any]:
    return PDFParser().extract_text(file_stream)