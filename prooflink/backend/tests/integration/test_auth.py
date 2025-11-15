"""
Integration tests for authentication endpoints
"""
import pytest


def test_register_user(client, test_user_data):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email"""
    # Register first user
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Try to register again with same email
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 400


def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Try to login with wrong password
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPassword123!"
    })
    
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with nonexistent user"""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "Password123!"
    })
    
    assert response.status_code == 401


def test_get_current_user(authenticated_client):
    """Test getting current user info"""
    response = authenticated_client.get("/api/v1/users/me")
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data


def test_unauthorized_access(client):
    """Test accessing protected endpoint without auth"""
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == 401