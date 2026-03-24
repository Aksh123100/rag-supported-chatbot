"""
Vector store service using FAISS for similarity search.
FAISS is more Windows-friendly and doesn't require C++ build tools.
"""
import os
import json
import pickle
from typing import List, Dict, Any, Optional
import uuid
import numpy as np
import faiss

from app.config import settings
from app.services.embedding import EmbeddingService


class VectorStoreService:
    """Service for managing vector database operations using FAISS."""

    def __init__(self):
        """Initialize vector store service."""
        self.embedding_service = EmbeddingService()
        self.dimension = self.embedding_service.get_embedding_dimension()

        # Ensure persist directory exists
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity with normalized vectors

        # Storage for documents and metadata
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []

        # Load existing data if available
        self._load_from_disk()

    def _get_index_path(self) -> str:
        """Get path for index file."""
        return os.path.join(settings.chroma_persist_directory, "faiss_index.bin")

    def _get_data_path(self) -> str:
        """Get path for data file."""
        return os.path.join(settings.chroma_persist_directory, "documents.pkl")

    def _save_to_disk(self):
        """Save index and documents to disk."""
        faiss.write_index(self.index, self._get_index_path())
        with open(self._get_data_path(), 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadatas': self.metadatas,
                'ids': self.ids
            }, f)

    def _load_from_disk(self):
        """Load index and documents from disk."""
        index_path = self._get_index_path()
        data_path = self._get_data_path()

        if os.path.exists(index_path) and os.path.exists(data_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadatas = data.get('metadatas', [])
                    self.ids = data.get('ids', [])
            except Exception as e:
                print(f"Warning: Could not load existing data: {e}")
                # Reset to empty state
                self.index = faiss.IndexFlatIP(self.dimension)
                self.documents = []
                self.metadatas = []
                self.ids = []

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts.
            metadatas: Optional list of metadata dictionaries.
            ids: Optional list of document IDs.

        Returns:
            List of document IDs.
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(documents)
        embeddings_array = np.array(embeddings).astype('float32')

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings_array)

        # Add to FAISS index
        self.index.add(embeddings_array)

        # Store documents and metadata
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)

        # Save to disk
        self._save_to_disk()

        return ids

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.

        Args:
            query_text: Query string.
            n_results: Number of results to return.
            where: Optional filter conditions (not implemented for FAISS version).

        Returns:
            Query results dictionary.
        """
        if len(self.documents) == 0:
            return {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }

        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query_text)
        query_array = np.array([query_embedding]).astype('float32')

        # Normalize for cosine similarity
        faiss.normalize_L2(query_array)

        # Search
        n_results = min(n_results, len(self.documents))
        distances, indices = self.index.search(query_array, n_results)

        # Format results
        result_ids = [[self.ids[i] for i in indices[0]]]
        result_documents = [[self.documents[i] for i in indices[0]]]
        result_metadatas = [[self.metadatas[i] for i in indices[0]]]
        result_distances = [[1 - d for d in distances[0]]]  # Convert to similarity

        return {
            'ids': result_ids,
            'documents': result_documents,
            'metadatas': result_metadatas,
            'distances': result_distances
        }

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store.
        Note: FAISS doesn't support efficient deletion, so we rebuild the index.

        Args:
            document_id: ID of document to delete.

        Returns:
            True if successful.
        """
        if document_id not in self.ids:
            return False

        # Find index
        idx = self.ids.index(document_id)

        # Remove from lists
        self.ids.pop(idx)
        self.documents.pop(idx)
        self.metadatas.pop(idx)

        # Rebuild index
        self.index = faiss.IndexFlatIP(self.dimension)
        if len(self.documents) > 0:
            embeddings = self.embedding_service.embed_texts(self.documents)
            embeddings_array = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings_array)
            self.index.add(embeddings_array)

        # Save to disk
        self._save_to_disk()

        return True

    def delete_by_metadata(self, key: str, value: str) -> bool:
        """
        Delete documents by metadata filter.

        Args:
            key: Metadata key.
            value: Metadata value.

        Returns:
            True if successful.
        """
        # Find indices to remove
        indices_to_remove = [
            i for i, meta in enumerate(self.metadatas)
            if meta.get(key) == value
        ]

        if not indices_to_remove:
            return False

        # Remove in reverse order to maintain indices
        for idx in reversed(indices_to_remove):
            self.ids.pop(idx)
            self.documents.pop(idx)
            self.metadatas.pop(idx)

        # Rebuild index
        self.index = faiss.IndexFlatIP(self.dimension)
        if len(self.documents) > 0:
            embeddings = self.embedding_service.embed_texts(self.documents)
            embeddings_array = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings_array)
            self.index.add(embeddings_array)

        # Save to disk
        self._save_to_disk()

        return True

    def get_document_count(self) -> int:
        """Get the total number of documents in the collection."""
        return len(self.documents)

    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents = []
        self.metadatas = []
        self.ids = []
        self._save_to_disk()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "collection_name": settings.chroma_collection_name,
            "document_count": len(self.documents),
            "persist_directory": settings.chroma_persist_directory,
            "embedding_dimension": self.dimension
        }