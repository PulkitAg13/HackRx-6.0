def get_llm_response(prompt: str) -> str:
    """
    Simulates getting a response from an LLM.
    Replace this function with a real API call to OpenAI, Azure, etc.
    """
    # Mock response for demo purposes
    if "cancellation" in prompt.lower():
        return "The clause states that the user can cancel the policy within 30 days."
    return "This clause pertains to general terms and conditions."

def parse_llm_response(response: str) -> dict:
    """
    Extracts structured information from raw LLM response text.
    """
    return {
        "summary": response,
        "confidence": 0.92  # mock value
    }
