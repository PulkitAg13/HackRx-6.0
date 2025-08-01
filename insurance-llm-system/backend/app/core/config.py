from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field, field_validator
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import yaml

# Load config file outside class definition
_config_path = Path(__file__).parent.parent.parent.parent / "config" / "settings.yaml"
_config: Dict[str, Any] = {}

if _config_path.exists():
    with open(_config_path, 'r', encoding='utf-8') as config_file:
        _config = yaml.safe_load(config_file) or {}
else:
    raise FileNotFoundError(f"Config file not found at {_config_path}")

class Settings(BaseSettings):
    # Application Config
    APP_ENV: str = Field(default=_config.get("app", {}).get("env", "development"))
    DEBUG: bool = Field(default=_config.get("app", {}).get("debug", True))
    API_KEY: str = Field(default=_config.get("app", {}).get("api_key", ""))
    CORS_ORIGINS: List[str] = Field(
        default=_config.get("app", {}).get("cors_origins", "*").split(",")
    )
    MAX_DOCUMENT_SIZE_MB: int = Field(
        default=_config.get("app", {}).get("max_file_size_mb", 10)
    )
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=_config.get("app", {}).get("allowed_file_types", ["pdf", "docx", "txt", "eml"])
    )

    # Document Processing
    PDF_MAX_PAGES: int = Field(default=_config.get("document_processing", {}).get("pdf_max_pages", 100))
    CHUNK_SIZE: int = Field(default=_config.get("document_processing", {}).get("chunk_size", 1000))
    CHUNK_OVERLAP: int = Field(default=_config.get("document_processing", {}).get("chunk_overlap", 200))

    # Cleaner Config
    CLEANER_LOWERCASE: bool = Field(
        default=_config.get("document_processing", {}).get("cleaner", {}).get("lowercase", True)
    )
    CLEANER_REMOVE_SPECIAL_CHARS: bool = Field(
        default=_config.get("document_processing", {}).get("cleaner", {}).get("remove_special_chars", True)
    )
    CLEANER_REMOVE_STOPWORDS: bool = Field(
        default=_config.get("document_processing", {}).get("cleaner", {}).get("remove_stopwords", False)
    )
    CLEANER_STOPWORDS: List[str] = Field(
        default=_config.get("document_processing", {}).get("cleaner", {}).get("stopwords", ["the", "and", "or"])
    )

    # Vector DB
    VECTOR_DB: str = Field(default=_config.get("vector_db", {}).get("type", "pinecone"))
    PINECONE_API_KEY: str = Field(default=_config.get("vector_db", {}).get("pinecone", {}).get("api_key", ""))
    PINECONE_ENVIRONMENT: str = Field(default=_config.get("vector_db", {}).get("pinecone", {}).get("environment", "us-west1-gcp"))
    PINECONE_INDEX_NAME: str = Field(default=_config.get("vector_db", {}).get("pinecone", {}).get("index_name", "insurance-docs"))
    CHROMA_COLLECTION_NAME: str = Field(default=_config.get("vector_db", {}).get("chroma", {}).get("collection_name", "insurance-clauses"))
    CHROMA_PERSIST_DIR: str = Field(default=_config.get("vector_db", {}).get("chroma", {}).get("persist_dir", "./chroma_db"))

    # Database Config
    DB_URL: str = Field(default="sqlite:///./insurance.db")  # SQLite database file
    TEST_DB_URL: Optional[str] = Field(default="sqlite:///./test.db")  # For testing
    DB_POOL_SIZE: int = Field(default=_config.get("database", {}).get("pool_size", 5))
    DB_MAX_OVERFLOW: int = Field(default=_config.get("database", {}).get("max_overflow", 10))

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    class Config:
        case_sensitive = True
        extra = "ignore"

settings = Settings()
