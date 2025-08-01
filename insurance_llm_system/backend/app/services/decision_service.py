import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from ..api.v1.schemas import ProcessResponse
from ml_models.llm_integration.model_selector import get_llm_response

logger = logging.getLogger(__name__)

def make_decision_from_clauses(
    query_analysis: Dict,
    relevant_clauses: List[Dict]
) -> Dict:
    """
    Make final insurance decision based on analyzed query and relevant clauses.
    Handles the complete decision logic and justification generation.
    """
    try:
        # Validate input data
        if not relevant_clauses:
            raise ValueError("No relevant clauses provided for decision making")
        
        # Generate decision prompt
        decision_prompt = build_decision_prompt(query_analysis, relevant_clauses)
        
        # Get LLM decision
        decision_result = get_structured_decision(decision_prompt)
        
        # Validate and format response
        validated_decision = validate_decision(decision_result)
        
        return validated_decision
    except Exception as e:
        logger.error(f"Decision making failed: {str(e)}")
        raise

def build_decision_prompt(query_analysis: Dict, relevant_clauses: List[Dict]) -> str:
    """Construct the decision prompt for the LLM"""
    clauses_text = "\n".join(
        f"Clause {i+1}:\n{clause['text']}\n(Section: {clause.get('section', 'N/A')})"
        for i, clause in enumerate(relevant_clauses)
    )
    
    return f"""
    As an insurance claim adjudicator, analyze this claim based on the policy clauses:
    
    Claim Details:
    - Age: {query_analysis.get('age', 'N/A')}
    - Gender: {query_analysis.get('gender', 'N/A')}
    - Procedure: {query_analysis.get('procedure', 'N/A')}
    - Location: {query_analysis.get('location', 'N/A')}
    - Policy Duration: {query_analysis.get('policy_duration_months', 'N/A')} months
    
    Relevant Policy Clauses:
    {clauses_text}
    
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