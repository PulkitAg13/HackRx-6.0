def format_response(query: str, matched_clauses: list[dict], decision: dict) -> dict:
    return {
        "query": query,
        "matched_clauses": matched_clauses,
        "decision": decision
    }
