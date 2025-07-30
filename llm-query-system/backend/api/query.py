# backend/api/query.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import json
import os

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
        # 🔹 Load embedded chunks from JSON file (use the same file created during upload)
        vector_store_path = "vector_store/embedded_data.json"
        if not os.path.exists(vector_store_path):
            raise HTTPException(status_code=404, detail="No embedded document found. Please upload first.")

        with open(vector_store_path, "r", encoding="utf-8") as f:
            embedded_data = json.load(f)

        documents = [item["chunk"] for item in embedded_data]

        # 🔹 Step 1: Search similar chunks
        relevant_chunks = search_similar_chunks(query, documents, top_k=5)

        if not relevant_chunks:
            return JSONResponse(content={"answer": "No relevant information found."})

        # 🔹 Step 2: Generate answer using LLM
        answer = generate_answer(query, relevant_chunks)

        return JSONResponse(content={"answer": answer, "context": relevant_chunks})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
