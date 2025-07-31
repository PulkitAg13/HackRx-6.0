from sqlalchemy.orm import Session
from . import models
from typing import Optional, List, Dict
import uuid

def create_document(db: Session, filename: str, file_type: str, file_size: int, metadata: dict = None):
    db_document = models.Document(
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        metadata=metadata or {}
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Document).offset(skip).limit(limit).all()

def create_clause(db: Session, document_id: int, clause_text: str, section: str = None, page_number: int = None, embeddings: list = None):
    db_clause = models.Clause(
        document_id=document_id,
        clause_text=clause_text,
        section=section,
        page_number=page_number,
        embeddings=embeddings
    )
    db.add(db_clause)
    db.commit()
    db.refresh(db_clause)
    return db_clause

def create_query(db: Session, document_id: int, raw_query: str, processed_query: dict = None):
    db_query = models.Query(
        document_id=document_id,
        raw_query=raw_query,
        processed_query=processed_query or {}
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def create_decision(db: Session, query_id: int, decision: str, amount: int = None, 
                   currency: str = "INR", confidence_score: float = None, justification: dict = None):
    db_decision = models.Decision(
        query_id=query_id,
        decision=decision,
        amount=amount,
        currency=currency,
        confidence_score=confidence_score,
        justification=justification or {}
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)
    return db_decision