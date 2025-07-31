from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import logging

from ...db import crud, models, session
from ...services.query_processor import process_insurance_query
from ...services.document_service import process_uploaded_document
from .schemas import (
    Query, QueryCreate, Decision, Document, DocumentCreate, Clause,
    ProcessResponse
)
from ...core.security import get_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/documents/", response_model=Document, tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(session.get_db),
    api_key: str = Depends(get_api_key)
):
    try:
        document = await process_uploaded_document(db, file)
        return document
    except ValueError as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/documents/", response_model=List[Document], tags=["documents"])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(session.get_db),
    api_key: str = Depends(get_api_key)
):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents

@router.post("/process/", response_model=ProcessResponse, tags=["queries"])
def process_query(
    query: QueryCreate,
    db: Session = Depends(session.get_db),
    api_key: str = Depends(get_api_key)
):
    try:
        # Store the raw query first
        db_query = crud.create_query(db, document_id=query.document_id, raw_query=query.raw_query)
        
        # Process the query
        result = process_insurance_query(db, query.raw_query, query.document_id)
        
        # Store the decision
        decision = crud.create_decision(
            db,
            query_id=db_query.id,
            decision=result.decision,
            amount=result.amount,
            currency=result.currency,
            confidence_score=result.confidence_score,
            justification=result.justification
        )
        
        response = ProcessResponse(
            decision=result.decision,
            amount=result.amount,
            currency=result.currency,
            justification=result.justification,
            confidence_score=result.confidence_score,
            query_id=db_query.id
        )
        
        return response
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/decisions/{query_id}", response_model=Decision, tags=["decisions"])
def read_decision(
    query_id: int,
    db: Session = Depends(session.get_db),
    api_key: str = Depends(get_api_key)
):
    decision = db.query(models.Decision).filter(models.Decision.query_id == query_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision