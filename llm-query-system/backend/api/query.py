# backend/api/query.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from services.embedding_search import search_similar_chunks
from services.llm_response import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/")
async def query_documents(request: QueryRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Step 1: Get top-k relevant chunks from vector DB
        relevant_chunks = search_similar_chunks(query, top_k=5)

        if not relevant_chunks:
            return JSONResponse(content={"answer": "No relevant information found."})

        # Step 2: Use LLM to generate answer
        answer = generate_answer(query, relevant_chunks)

        return JSONResponse(content={"answer": answer, "context": relevant_chunks})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
