"""
Tests for document endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestDocumentUpload:
    """Tests for document upload endpoints."""

    def test_upload_document_endpoint_exists(self, client):
        """Test that upload endpoint exists."""
        response = client.post(
            "/api/v1/documents/upload",
            json={
                "content": "Test content",
                "metadata": {
                    "source": "test.txt",
                    "category": "test"
                }
            }
        )
        # Should not return 404
        assert response.status_code != 404

    def test_upload_requires_content(self, client):
        """Test that upload requires content."""
        response = client.post(
            "/api/v1/documents/upload",
            json={
                "metadata": {
                    "source": "test.txt"
                }
            }
        )
        assert response.status_code == 422

    def test_upload_requires_metadata_source(self, client):
        """Test that upload requires source in metadata."""
        response = client.post(
            "/api/v1/documents/upload",
            json={
                "content": "Test content",
                "metadata": {}
            }
        )
        assert response.status_code == 422


class TestDocumentSearch:
    """Tests for document search endpoint."""

    def test_search_endpoint_exists(self, client):
        """Test that search endpoint exists."""
        response = client.post(
            "/api/v1/documents/search",
            json={"query": "test"}
        )
        # Should not return 404
        assert response.status_code != 404

    def test_search_requires_query(self, client):
        """Test that search requires query."""
        response = client.post(
            "/api/v1/documents/search",
            json={}
        )
        assert response.status_code == 422

    def test_search_top_k_optional(self, client):
        """Test that top_k is optional."""
        response = client.post(
            "/api/v1/documents/search",
            json={"query": "test"}
        )
        # Should not fail validation
        assert response.status_code != 422


class TestDocumentStats:
    """Tests for document stats endpoint."""

    def test_stats_endpoint_exists(self, client):
        """Test that stats endpoint exists."""
        response = client.get("/api/v1/documents/stats")
        # Should not return 404
        assert response.status_code != 404


class TestDocumentDeletion:
    """Tests for document deletion endpoints."""

    def test_delete_endpoint_exists(self, client):
        """Test that delete endpoint exists."""
        response = client.delete("/api/v1/documents/test-id")
        # Should not return 404
        assert response.status_code != 404

    def test_clear_endpoint_exists(self, client):
        """Test that clear endpoint exists."""
        response = client.delete("/api/v1/documents/clear")
        # Should not return 404
        assert response.status_code != 404