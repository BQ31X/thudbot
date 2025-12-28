#!/usr/bin/env python3
"""
Smoke tests for Retrieval Service API
Tests that the HTTP endpoint is functional and returns expected structure.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the retrieval API."""
    from retrieval_service.api import app
    return TestClient(app)


def test_retrieve_endpoint_exists(client):
    """Verify /retrieve endpoint exists and fails predictably."""
    response = client.post(
        "/retrieve",
        json={"query": "test query", "k": 1}
    )
    # 200 = success, 422 = validation error, 503 = Qdrant unavailable
    assert response.status_code in (200, 422, 503), \
        f"Unexpected status code: {response.status_code}"


def test_retrieve_response_structure(client):
    """Verify /retrieve returns expected JSON structure."""
    response = client.post(
        "/retrieve",
        json={"query": "How do I save the game?", "k": 1}
    )
    
    # Should always return JSON (even on errors)
    assert response.headers["content-type"].startswith("application/json"), \
        f"Expected JSON, got: {response.headers.get('content-type')}"
    
    # If successful, validate structure
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict), "Response should be a dict"
        assert "documents" in data, "Response missing 'documents' key"
        assert isinstance(data["documents"], list), "'documents' should be a list"


def test_retrieve_with_invalid_payload(client):
    """Verify /retrieve handles invalid payloads gracefully."""
    # Missing required fields
    response = client.post("/retrieve", json={})
    assert response.status_code == 422, "Should reject invalid payload"


def test_retrieve_k_parameter(client):
    """Verify /retrieve respects the k parameter."""
    response = client.post(
        "/retrieve",
        json={"query": "test", "k": 5}
    )
    
    # If successful and Qdrant has data, check k is respected
    if response.status_code == 200:
        data = response.json()
        # Should return at most k documents
        assert len(data["documents"]) <= 5, "Returned more documents than requested"


@pytest.mark.skip(reason="Requires running Qdrant with populated collection")
def test_retrieve_with_real_query(client):
    """
    Integration test: Verify /retrieve returns relevant results.
    
    This test requires:
    - Qdrant running at QDRANT_URL
    - Collection exists with game hint data
    - Embedding provider configured (OpenAI or local BGE)
    """
    response = client.post(
        "/retrieve",
        json={"query": "How do I save the game?", "k": 3}
    )
    
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()
    
    assert len(data["documents"]) > 0, "Should return at least one document"
    assert "save" in data["documents"][0].lower(), "Result should be relevant to 'save'"

