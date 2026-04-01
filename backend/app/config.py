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

    # OpenAI Configuration (fallback)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Ollama Configuration (free local LLM)
    use_ollama: bool = os.getenv("USE_OLLAMA", "False").lower() == "true"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen2.5:7b")
    
    # Google Gemini Configuration
    use_gemini: bool = os.getenv("USE_GEMINI", "False").lower() == "true"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Groq Configuration (FREE & FAST!)
    use_groq: bool = os.getenv("USE_GROQ", "False").lower() == "true"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ChromaDB Configuration
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "support_docs")

    # Application Settings
    app_name: str = os.getenv("APP_NAME", "RAG Support Chatbot")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    # CORS Settings
    cors_origins: List[str] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from environment (JSON array format)
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            import json
            try:
                self.cors_origins = json.loads(cors_env)
            except json.JSONDecodeError:
                # Fallback to comma-separated list
                self.cors_origins = [origin.strip() for origin in cors_env.split(",")]
        else:
            # Default for local development
            self.cors_origins = ["http://localhost:3000", "http://localhost:5173"]

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