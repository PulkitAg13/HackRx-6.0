from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    document_metadata = Column(JSON)  # Changed from 'metadata' to avoid conflict
    
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="document", cascade="all, delete-orphan")

class Clause(Base):
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    clause_text = Column(String, nullable=False)
    section = Column(String)
    page_number = Column(Integer)
    embeddings = Column(JSON)  # Consider storing vector embeddings separately
    
    document = relationship("Document", back_populates="clauses")

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    raw_query = Column(String, nullable=False)
    processed_query = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="queries")
    decisions = relationship("Decision", back_populates="query", cascade="all, delete-orphan")

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"))
    decision = Column(String, nullable=False)
    amount = Column(Integer)
    currency = Column(String, default="INR")
    confidence_score = Column(Integer)
    justification = Column(JSON)  # Consider using a proper JSON schema
    
    query = relationship("Query", back_populates="decisions")