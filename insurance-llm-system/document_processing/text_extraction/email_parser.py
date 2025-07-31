import logging
import email
from email import policy
from email.parser import BytesParser
from io import BytesIO
from typing import Dict, Optional
from ...backend.app.core.config import settings

logger = logging.getLogger(__name__)

class EmailParser:
    def extract_text(self, file_stream: BytesIO) -> Dict[str, any]:
        """
        Extract content and metadata from email
        Returns:
            {
                "text": str,
                "metadata": {
                    "subject": str,
                    "from": str,
                    "to": str,
                    "date": str,
                    "attachments": List[Dict]
                }
            }
        """
        try:
            msg = BytesParser(policy=policy.default).parse(file_stream)
            
            # Extract metadata
            metadata = {
                "subject": msg.get("Subject", ""),
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "date": msg.get("Date", ""),
                "attachments": []
            }
            
            # Extract text content
            text_parts = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    text_parts.append(part.get_content())
                elif part.get_content_maintype() != "multipart" and part.get_filename():
                    metadata["attachments"].append({
                        "filename": part.get_filename(),
                        "content_type": part.get_content_type(),
                        "size": len(part.get_payload(decode=True))
                    })
            
            return {
                "text": "\n".join(text_parts),
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Email parsing failed: {str(e)}")
            raise

def parse_email(file_stream: BytesIO) -> Dict[str, any]:
    return EmailParser().extract_text(file_stream)