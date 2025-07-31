from pydantic_settings import BaseSettings
from pydantic import AnyUrl, validator
from typing import List, Optional
import os
from pathlib import Path
import yaml

class Settings(BaseSettings):
    # Load from YAML config
    with open(Path(__file__).parent.parent.parent / "config" / "settings.yaml") as f:
        config = yaml.safe_load(f)

    # Application Config
    APP_ENV: str = config["app"]["env"]
    DEBUG: bool = config["app"]["debug"]
    CORS_ORIGINS: List[str] = config["app"]["cors_origins"].split(",")
    API_KEY: str = config["app"]["api_key"]
    
    # Document Processing
    MAX_DOCUMENT_SIZE_MB: int = config["app"]["max_file_size_mb"]
    ALLOWED_FILE_TYPES: List[str] = config["app"]["allowed_file_types"]
    PDF_MAX_PAGES: int = config["document_processing"]["pdf_max_pages"]
    CHUNK_SIZE: int = config["document_processing"]["chunk_size"]
    CHUNK_OVERLAP: int = config["document_processing"]["chunk_overlap"]
    
    # Vector DB
    VECTOR_DB: str = config["vector_db"]["type"]
    PINECONE_API_KEY: str = config["vector_db"]["pinecone"]["api_key"]
    PINECONE_ENVIRONMENT: str = config["vector_db"]["pinecone"]["environment"]
    PINECONE_INDEX_NAME: str = config["vector_db"]["pinecone"]["index_name"]
    CHROMA_COLLECTION_NAME: str = config["vector_db"]["chroma"]["collection_name"]
    
    # Database Config
    DB_URL: AnyUrl = os.getenv("DB_URL", "postgresql://user:password@localhost:5432/insurance_db")
    TEST_DB_URL: Optional[AnyUrl] = None
    
    class Config:
        case_sensitive = True

settings = Settings()