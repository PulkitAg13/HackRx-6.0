import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..db import crud
from ....ml_models.llm_integration.openai_integration import get_llm_response  # Changed from models.llm_integration
from ..api.v1.schemas import ProcessResponse

logger = logging.getLogger(__name__)

def make_decision_from_clauses(
    db: Session,
    query_analysis: Dict,
    relevant_clauses: List[Dict],
    document_id: int
) -> ProcessResponse:
    """
    Make final insurance decision based on analyzed query and relevant clauses.
    Handles the complete decision logic and justification generation.
    """
    try:
        # Step 1: Validate input data
        if not relevant_clauses:
            raise ValueError("No relevant clauses provided for decision making")
        
        # Step 2: Generate decision prompt
        decision_prompt = build_decision_prompt(query_analysis, relevant_clauses)
        
        # Step 3: Get LLM decision
        decision_result = get_structured_decision(decision_prompt)
        
        # Step 4: Validate and format response
        validated_decision = validate_decision(decision_result)
        
        return ProcessResponse(
            decision=validated_decision["decision"],
            amount=validated_decision.get("amount"),
            currency=validated_decision.get("currency", "INR"),
            justification=validated_decision["justification"],
            confidence_score=validated_decision.get("confidence_score", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Decision making failed: {str(e)}")
        raise

def build_decision_prompt(query_analysis: Dict, relevant_clauses: List[Dict]) -> str:
    """Construct the decision prompt for the LLM"""
    return f"""
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

def format_clauses_for_prompt(clauses: List[Dict]) -> str:
    """Format clauses for the decision prompt"""
    return "\n".join(
        f"Clause {idx+1} (Section {clause.get('section', 'N/A')}): {clause['text']}"
        for idx, clause in enumerate(clauses)
    )

def get_structured_decision(prompt: str) -> Dict:
    """Get structured decision from LLM with validation"""
    response = get_llm_response(
        prompt,
        response_format="json_object",
        temperature=0.2  # Keep responses deterministic
    )
    
    if not isinstance(response, dict):
        raise ValueError("LLM returned invalid decision format")
    
    return response

def validate_decision(decision: Dict) -> Dict:
    """Validate the decision structure and values"""
    required_fields = ["decision", "justification"]
    for field in required_fields:
        if field not in decision:
            raise ValueError(f"Missing required decision field: {field}")
    
    decision["decision"] = decision["decision"].lower()
    if decision["decision"] not in ["approved", "denied", "pending"]:
        raise ValueError("Invalid decision value")
    
    if "amount" in decision and decision["amount"] is not None:
        try:
            decision["amount"] = float(decision["amount"])
        except (ValueError, TypeError):
            raise ValueError("Invalid amount value")
    
    if "confidence_score" in decision:
        try:
            confidence = float(decision["confidence_score"])
            if not 0 <= confidence <= 1:
                raise ValueError("Confidence score must be between 0 and 1")
            decision["confidence_score"] = confidence
        except (ValueError, TypeError):
            raise ValueError("Invalid confidence score")
    
    return decision