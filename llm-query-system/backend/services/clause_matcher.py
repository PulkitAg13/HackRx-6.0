def match_clause_to_query(clause: str, query: str) -> bool:
    return query.lower() in clause.lower()
