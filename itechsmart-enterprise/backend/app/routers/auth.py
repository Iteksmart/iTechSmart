"""
Authentication Router
Handles user authentication and authorization
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """User login endpoint"""
    # In production, verify credentials against database
    if (
        credentials.email == "admin@itechsmart.dev"
        and credentials.password == "admin123"
    ):
        return TokenResponse(
            access_token="mock-jwt-token-replace-in-production",
            token_type="bearer",
            expires_in=3600,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )


@router.post("/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user():
    """Get current user information"""
    return {
        "id": 1,
        "email": "admin@itechsmart.dev",
        "name": "Admin User",
        "role": "admin",
    }
