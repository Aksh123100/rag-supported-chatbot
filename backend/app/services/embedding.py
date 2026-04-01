"""
Embedding service using Voyage AI (free cloud API, fast).
"""
from typing import List
import voyageai
import os


class EmbeddingService:
    """Service for generating embeddings using Voyage AI."""

    def __init__(self):
        """Initialize embedding service with Voyage AI."""
        api_key = os.getenv("VOYAGE_API_KEY", "pa-Z9tLIIroFUuajg7QKG580xDXiulLNaZTUIOP5K5MwRt")
        self.client = voyageai.Client(api_key=api_key)
        self.model = "voyage-3-lite"  # Fast, free tier friendly

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        result = self.client.embed(texts, model=self.model, input_type="document")
        return result.embeddings

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        result = self.client.embed([query], model=self.model, input_type="query")
        return result.embeddings[0]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return 512  # voyage-3-lite dimension