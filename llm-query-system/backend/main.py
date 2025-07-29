# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine
from db import models
from api import upload, query, health

# Create DB tables (safe to leave for dev)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LLM Clause Matcher API",
    description="Upload documents, ask natural language queries, and get matched clauses.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(health.router, tags=["Health"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "LLM Clause Matcher API is running."}

