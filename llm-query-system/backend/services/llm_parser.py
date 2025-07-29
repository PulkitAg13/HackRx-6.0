def extract_relevant_info_from_chunk(chunk: str) -> dict:
    # This should ideally call an actual LLM API like OpenAI
    # For now, return mock data
    return {
        "clause": "Cancellation Policy",
        "content": chunk[:200],  # first 200 characters
        "relevance_score": 0.9
    }
