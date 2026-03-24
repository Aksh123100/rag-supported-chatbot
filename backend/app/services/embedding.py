"""
Embedding service for generating text embeddings.
"""
from typing import List
from openai import OpenAI
from app.config import settings


class EmbeddingService:
    """Service for generating embeddings using OpenAI."""

    def __init__(self):
        """Initialize embedding service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors.
        """
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query string to embed.

        Returns:
            Embedding vector.
        """
        response = self.client.embeddings.create(
            input=query,
            model=self.model
        )
        return response.data[0].embedding

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for the current model."""
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        return dimensions.get(self.model, 1536)