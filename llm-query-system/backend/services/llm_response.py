def generate_answer(query: str, context_chunks: list[tuple[str, float]]) -> str:
    """
    Simulates generating an answer using an LLM based on the query and relevant context.
    Replace with actual API integration later.
    """
    context = " ".join(chunk for chunk, _ in context_chunks)
    prompt = f"Answer the following question based on the context:\n\nContext:\n{context}\n\nQuestion: {query}"

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
