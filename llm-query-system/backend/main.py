# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import engine
from .db import models
from .api import upload, query, health

# Create tables (optional depending on your migration strategy)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LLM Clause Matcher API",
    description="Upload documents, ask natural language queries, and get matched clauses.",
    version="1.0.0",
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route includes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(health.router, tags=["Health"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "LLM Clause Matcher API is running."}
