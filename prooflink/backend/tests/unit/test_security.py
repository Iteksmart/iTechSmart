"""
Unit tests for security functions
"""
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    # Hash should be different from password
    assert hashed != password
    
    # Verification should succeed
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_creation():
    """Test JWT token creation"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    
    # Token should have 3 parts (header.payload.signature)
    assert len(token.split('.')) == 3


def test_token_verification():
    """Test JWT token verification"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    # Verification should succeed
    payload = verify_token(token)
    assert payload is not None
    assert payload.get("sub") == "test@example.com"


def test_invalid_token_verification():
    """Test invalid token verification"""
    invalid_token = "invalid.token.here"
    
    # Verification should fail
    payload = verify_token(invalid_token)
    assert payload is None