def determine_outcome(matched_clauses: list[dict]) -> dict:
    # Very basic rule engine logic
    for clause in matched_clauses:
        if "rejection" in clause["content"].lower():
            return {"approved": False, "reason": "Clause indicates rejection"}
    return {"approved": True, "reason": "No rejecting clause found"}
