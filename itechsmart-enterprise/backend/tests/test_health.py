"""
Basic health check tests for iTechSmart Enterprise
"""

import pytest


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_root(client):
    """Test API root endpoint"""
    response = client.get("/api/v1/")

    assert response.status_code in [200, 404]  # May or may not exist
