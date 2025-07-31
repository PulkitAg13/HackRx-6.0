from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class QueryBase(BaseModel):
    raw_query: str
    document_id: int

class QueryCreate(QueryBase):
    pass

class Query(QueryBase):
    id: int
    processed_query: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        orm_mode = True

class DecisionBase(BaseModel):
    decision: str
    amount: Optional[int]
    currency: Optional[str]
    confidence_score: Optional[float]
    justification: Dict[str, Any]

class DecisionCreate(DecisionBase):
    query_id: int

class Decision(DecisionBase):
    id: int
    query_id: int
    
    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    metadata: Optional[Dict[str, Any]] = {}

class Document(DocumentBase):
    id: int
    upload_date: datetime
    processed: bool
    metadata: Dict[str, Any]
    
    class Config:
        orm_mode = True

class ClauseBase(BaseModel):
    clause_text: str
    document_id: int
    section: Optional[str]
    page_number: Optional[int]

class ClauseCreate(ClauseBase):
    pass

class Clause(ClauseBase):
    id: int
    
    class Config:
        orm_mode = True

class ProcessResponse(BaseModel):
    decision: str
    amount: Optional[int]
    currency: Optional[str]
    justification: Dict[str, Any]
    confidence_score: Optional[float]
    query_id: int