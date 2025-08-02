from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional, Union,Literal
import os

class Settings(BaseSettings):
    # Application Configuration
    APP_ENV: str = Field(
        default="development",
        description="Application environment (development|production|staging)"
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode (verbose logging, error details)"
    )
    API_KEY: str = Field(
        default="",
        description="API key for service authentication"
    )

    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default=["http://localhost:3000"],
        description="List of allowed CORS origins (comma-separated or JSON list in .env)"
    )

    # Document Processing Configuration
    MAX_DOCUMENT_SIZE_MB: int = Field(
        default=10,
        description="Maximum document size in megabytes"
    )
    ALLOWED_FILE_TYPES: Union[str, List[str]] = Field(
        default=["pdf", "docx", "txt"],
        description="Supported file extensions"
    )
    CHUNK_SIZE: int = Field(
        default=1000,
        description="Character count for text chunking"
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Character overlap between chunks"
    )

    PDF_MAX_PAGES: int = 20
    PDF_MAX_SIZE_MB: int = 10
    CLEANER_CONFIG: dict[str, str] = {
        "remove_headers": "true",
        "normalize_spacing": "true"
    }

    # Database Configuration
    DB_URL: str = Field(
        default="sqlite:///./insurance.db",
        description="Database connection URL"
    )
    TEST_DB_URL: Optional[str] = Field(
        default=None,
        description="Test database connection URL"
    )

    # Vector Database Configuration
    VECTOR_DB: str = Field(
        default="pinecone",
        description="Vector database provider (pinecone|chroma)"
    )
    PINECONE_API_KEY: str = Field(
        default="",
        description="Pinecone API key"
    )
    PINECONE_ENVIRONMENT: str = Field(
        default="us-west1-gcp",
        description="Pinecone environment"
    )
    PINECONE_INDEX_NAME: str = Field(
        default="insurance-docs",
        description="Pinecone index name"
    )

    # LLM Configuration
    LLM_PROVIDER: Literal['openai', 'llama'] = Field(
        default='openai',
        description="Which LLM provider to use (openai|llama)"
    )
    USE_LOCAL_LLM: bool = Field(
        default=False,
        description="Whether to use a local LLM (Llama 2)"
    )
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4-1106-preview",
        description="OpenAI model name"
    )
    LLAMA_MODEL_PATH: str = Field(
        default="",
        description="Path to local Llama model"
    )

    @field_validator("CORS_ORIGINS", "ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_list(cls, v):
        """Support comma-separated strings or JSON arrays from .env"""
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            try:
                # Try to parse JSON list (e.g., '["http://localhost"]')
                import json
                return json.loads(v)
            except Exception:
                # Fallback to comma-split
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False  # Allow case-insensitive env vars

# Instantiate settings
settings = Settings()
