"""
Shared dependencies for the application.
"""
from app.services.vectorstore import VectorStoreService
from app.services.llm import LLMService

# Singleton instances shared across all routers
_vector_store = None
_llm_service = None


def get_vector_store() -> VectorStoreService:
    """Get the shared vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store


def get_llm_service() -> LLMService:
    """Get the shared LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
