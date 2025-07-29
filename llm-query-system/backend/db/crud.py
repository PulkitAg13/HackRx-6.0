from sqlalchemy.orm import Session
from . import models

def create_uploaded_document(db: Session, filename: str, content: str):
    doc = models.UploadedDocument(filename=filename, content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_uploaded_documents(db: Session):
    return db.query(models.UploadedDocument).all()

def log_query(db: Session, query: str, response: str):
    log = models.QueryLog(query=query, response=response)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
