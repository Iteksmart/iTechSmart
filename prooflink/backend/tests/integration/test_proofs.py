"""
Integration tests for proof endpoints
"""

import pytest
from io import BytesIO


def test_create_proof(authenticated_client):
    """Test creating a proof"""
    proof_data = {
        "title": "Test Proof",
        "type": "text",
        "content": "This is test content",
    }

    response = authenticated_client.post("/api/v1/proofs", json=proof_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == proof_data["title"]
    assert data["type"] == proof_data["type"]
    assert "id" in data
    assert "proof_link" in data
    assert "file_hash" in data


def test_get_proof(authenticated_client):
    """Test getting a proof by ID"""
    # Create proof first
    proof_data = {
        "title": "Test Proof",
        "type": "text",
        "content": "This is test content",
    }
    create_response = authenticated_client.post("/api/v1/proofs", json=proof_data)
    proof_id = create_response.json()["id"]

    # Get proof
    response = authenticated_client.get(f"/api/v1/proofs/{proof_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == proof_id
    assert data["title"] == proof_data["title"]


def test_list_proofs(authenticated_client):
    """Test listing proofs"""
    # Create multiple proofs
    for i in range(3):
        proof_data = {
            "title": f"Test Proof {i}",
            "type": "text",
            "content": f"Content {i}",
        }
        authenticated_client.post("/api/v1/proofs", json=proof_data)

    # List proofs
    response = authenticated_client.get("/api/v1/proofs")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_verify_proof(client, authenticated_client):
    """Test verifying a proof"""
    # Create proof first
    proof_data = {
        "title": "Test Proof",
        "type": "text",
        "content": "This is test content",
    }
    create_response = authenticated_client.post("/api/v1/proofs", json=proof_data)
    proof_id = create_response.json()["id"]

    # Verify proof (public endpoint)
    response = client.get(f"/api/v1/proofs/{proof_id}/verify")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "timestamp" in data


def test_delete_proof(authenticated_client):
    """Test deleting a proof"""
    # Create proof first
    proof_data = {
        "title": "Test Proof",
        "type": "text",
        "content": "This is test content",
    }
    create_response = authenticated_client.post("/api/v1/proofs", json=proof_data)
    proof_id = create_response.json()["id"]

    # Delete proof
    response = authenticated_client.delete(f"/api/v1/proofs/{proof_id}")

    assert response.status_code == 204

    # Verify proof is deleted
    get_response = authenticated_client.get(f"/api/v1/proofs/{proof_id}")
    assert get_response.status_code == 404


def test_unauthorized_proof_access(client):
    """Test accessing proofs without authentication"""
    response = client.get("/api/v1/proofs")

    assert response.status_code == 401
