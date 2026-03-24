"""
Tests for chat endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestChatEndpoint:
    """Tests for the chat endpoint."""

    def test_chat_endpoint_exists(self, client):
        """Test that the chat endpoint exists."""
        response = client.post("/api/v1/chat/quick?query=test")
        # Should not return 404
        assert response.status_code != 404

    def test_chat_requires_query(self, client):
        """Test that quick chat requires a query parameter."""
        response = client.post("/api/v1/chat/quick")
        assert response.status_code == 422  # Validation error

    def test_chat_with_empty_query(self, client):
        """Test chat with empty query."""
        response = client.post("/api/v1/chat", json={"query": ""})
        assert response.status_code == 422  # Validation error

    def test_chat_with_valid_query_structure(self, client):
        """Test that valid query structure is accepted."""
        # This test checks structure, not actual response
        # since it depends on external services
        response = client.post(
            "/api/v1/chat",
            json={
                "query": "What is the return policy?",
                "conversation_history": None,
                "top_k": 5
            }
        )
        # Should be accepted (not validation error)
        assert response.status_code != 422


class TestChatRequest:
    """Tests for chat request validation."""

    def test_max_query_length(self, client):
        """Test that query has max length."""
        long_query = "a" * 5000  # Exceeds max of 4000
        response = client.post(
            "/api/v1/chat",
            json={"query": long_query}
        )
        assert response.status_code == 422

    def test_top_k_bounds(self, client):
        """Test that top_k must be between 1 and 20."""
        # Too low
        response = client.post(
            "/api/v1/chat",
            json={"query": "test", "top_k": 0}
        )
        assert response.status_code == 422

        # Too high
        response = client.post(
            "/api/v1/chat",
            json={"query": "test", "top_k": 25}
        )
        assert response.status_code == 422

        # Valid
        response = client.post(
            "/api/v1/chat",
            json={"query": "test", "top_k": 10}
        )
        assert response.status_code != 422