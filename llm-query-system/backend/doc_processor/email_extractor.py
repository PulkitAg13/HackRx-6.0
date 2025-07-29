from email import policy
from email.parser import BytesParser

def extract_text_from_email(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    if msg.is_multipart():
        parts = [part.get_payload(decode=True).decode(errors="ignore")
                 for part in msg.walk()
                 if part.get_content_type() == "text/plain"]
        return "\n".join(parts)
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
