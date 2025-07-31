from pydantic import BaseSettings, AnyUrl, validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application Config
    APP_ENV: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database Config
    DB_URL: AnyUrl = "postgresql://user:password@localhost:5432/insurance_db"
    TEST_DB_URL: Optional[AnyUrl] = None
    
    # LLM Config
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-1106-preview"
    
    # Vector DB Config
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "insurance-docs"
    
    # Document Processing
    MAX_DOCUMENT_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()