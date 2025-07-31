import logging
from typing import Optional
from sqlalchemy.orm import Session
from ..db import crud
from ....ml_models.llm_integration.openai_integration import get_llm_response
from ....ml_models.embedding_models.ada_embeddings import get_embeddings
from ....document_processing.vector_db import search_clauses
from ..api.v1.schemas import ProcessResponse

logger = logging.getLogger(__name__)

def process_insurance_query(db: Session, query: str, document_id: int) -> ProcessResponse:
    """
    Process an insurance query through the full pipeline:
    1. Query understanding
    2. Relevant clause retrieval
    3. Decision making
    4. Justification generation
    """
    try:
        # Step 1: Query Understanding
        query_analysis = analyze_query(query)
        
        # Step 2: Retrieve relevant clauses
        relevant_clauses = retrieve_relevant_clauses(db, document_id, query_analysis)
        
        # Step 3: Make decision based on clauses
        decision_result = make_decision(query_analysis, relevant_clauses)
        
        return ProcessResponse(
            decision=decision_result["decision"],
            amount=decision_result.get("amount"),
            currency=decision_result.get("currency", "INR"),
            justification=decision_result["justification"],
            confidence_score=decision_result.get("confidence_score", 0.0)
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise

def analyze_query(query: str) -> dict:
    """Extract structured information from natural language query"""
    prompt = f"""
    Extract the following information from this insurance query:
    Query: {query}
    
    Extract as JSON with these fields:
    - age: number or null
    - gender: string (M/F) or null
    - procedure: string or null
    - location: string or null
    - policy_duration_months: number or null
    - other_details: object or null
    """
    
    response = get_llm_response(prompt, response_format="json_object")
    return response

def retrieve_relevant_clauses(db: Session, document_id: int, query_analysis: dict) -> list:
    """Retrieve relevant clauses from the document based on query analysis"""
    # Get query embedding
    query_embedding = get_embeddings(str(query_analysis))
    
    # Search vector DB for relevant clauses
    clause_ids = search_clauses(document_id, query_embedding, top_k=5)
    
    # Get full clause texts from database
    clauses = []
    for clause_id in clause_ids:
        clause = crud.get_clause(db, clause_id)
        if clause:
            clauses.append({
                "id": clause.id,
                "text": clause.clause_text,
                "section": clause.section,
                "page": clause.page_number
            })
    
    return clauses

def make_decision(query_analysis: dict, relevant_clauses: list) -> dict:
    """Make insurance decision based on query and relevant clauses"""
    decision_prompt = f"""
    You are an insurance claim adjudicator. Based on the following query analysis and policy clauses, 
    determine if the claim should be approved or rejected, and calculate the appropriate amount if applicable.
    
    Query Analysis:
    {query_analysis}
    
    Relevant Policy Clauses:
    {relevant_clauses}
    
    Provide your response as JSON with these fields:
    - decision: string (approved/denied/pending)
    - amount: number or null
    - currency: string (default: INR)
    - justification: object mapping each part of decision to specific clauses
    - confidence_score: float (0-1)
    """
    
    response = get_llm_response(decision_prompt, response_format="json_object")
    return response