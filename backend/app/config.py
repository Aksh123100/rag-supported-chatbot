"""
Application configuration settings.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # ChromaDB Configuration
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "support_docs")

    # Application Settings
    app_name: str = os.getenv("APP_NAME", "RAG Support Chatbot")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Chunking Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Retrieval Settings
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()