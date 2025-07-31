import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..db import crud
from ml_models.llm_integration.model_selector import get_llm_response
from ml_models.embedding_models.model_selector import get_embeddings
from ml_models.vector_db.vector_db_selector import search_clauses
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
        logger.info(f"Query analysis completed: {query_analysis}")
        
        # Step 2: Retrieve relevant clauses
        relevant_clauses = retrieve_relevant_clauses(db, document_id, query_analysis)
        if not relevant_clauses:
            raise ValueError("No relevant clauses found for query")
        logger.info(f"Retrieved {len(relevant_clauses)} relevant clauses")
        
        # Step 3: Make decision based on clauses
        decision_result = make_decision(query_analysis, relevant_clauses)
        logger.info(f"Decision made: {decision_result.decision}")
        
        return ProcessResponse(
            decision=decision_result["decision"],
            amount=decision_result.get("amount"),
            currency=decision_result.get("currency", "INR"),
            justification=decision_result["justification"],
            confidence_score=decision_result.get("confidence_score", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise

def analyze_query(query: str) -> Dict:
    """Extract structured information from natural language query"""
    prompt = f"""
    Analyze this insurance query and extract relevant details:
    Query: "{query}"
    
    Extract as JSON with these fields:
    - age: number|null
    - gender: string (M/F/Other)|null
    - procedure: string|null
    - location: string|null
    - policy_duration_months: number|null
    - other_details: object|null
    """
    
    response = get_llm_response(
        prompt,
        response_format="json_object",
        temperature=0.1
    )
    
    if not isinstance(response, dict):
        raise ValueError("LLM returned invalid query analysis format")
    
    return response

def retrieve_relevant_clauses(db: Session, document_id: int, query_analysis: Dict) -> List[Dict]:
    """Retrieve relevant clauses from the document based on query analysis"""
    # Create semantic search query
    search_query = build_semantic_query(query_analysis)
    
    # Get query embedding
    query_embedding = get_embeddings(search_query)
    
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
                "page_number": clause.page_number
            })
    
    return clauses

def build_semantic_query(query_analysis: Dict) -> str:
    """Build a good semantic search query from the analysis"""
    parts = []
    if query_analysis.get("procedure"):
        parts.append(f"Procedure: {query_analysis['procedure']}")
    if query_analysis.get("location"):
        parts.append(f"Location: {query_analysis['location']}")
    if query_analysis.get("policy_duration_months"):
        parts.append(f"Policy duration: {query_analysis['policy_duration_months']} months")
    if query_analysis.get("age"):
        parts.append(f"Age: {query_analysis['age']}")
    
    return "; ".join(parts) if parts else str(query_analysis)

def make_decision(query_analysis: Dict, relevant_clauses: List[Dict]) -> Dict:
    """Make insurance decision based on query and relevant clauses"""
    decision_prompt = f"""
    As an insurance claim adjudicator, analyze this claim based on the policy clauses:
    
    Claim Details:
    - Age: {query_analysis.get('age', 'N/A')}
    - Gender: {query_analysis.get('gender', 'N/A')}
    - Procedure: {query_analysis.get('procedure', 'N/A')}
    - Location: {query_analysis.get('location', 'N/A')}
    - Policy Duration: {query_analysis.get('policy_duration_months', 'N/A')} months
    
    Relevant Policy Clauses:
    {format_clauses_for_prompt(relevant_clauses)}
    
    Provide your decision in this JSON format:
    {{
        "decision": "approved|denied|pending",
        "amount": number|null,
        "currency": "INR",
        "justification": {{
            "coverage": "Which clause covers this?",
            "limitations": "Any limitations that apply",
            "requirements": "Requirements met/missing"
        }},
        "confidence_score": 0.0-1.0
    }}
    """
    
    response = get_llm_response(
        decision_prompt,
        response_format="json_object",
        temperature=0.2
    )
    return response

def format_clauses_for_prompt(clauses: List[Dict]) -> str:
    """Format clauses for the decision prompt"""
    return "\n".join(
        f"Clause {idx+1} (Section {clause.get('section', 'N/A')}): {clause['text']}"
        for idx, clause in enumerate(clauses)
    )