# core/config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "LLM Clause Search System"
    environment: str = "development"
    debug: bool = True

    # Add any other configs here (e.g., database, API keys later)

    class Config:
        env_file = ".env"

settings = Settings()
