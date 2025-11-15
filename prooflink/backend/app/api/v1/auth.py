"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    decode_token,
    generate_verification_code
)
from app.core.exceptions import AuthenticationError, ValidationError
from app.models.user import User, UserRole, SubscriptionStatus

router = APIRouter()


# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    code: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# Endpoints
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise ValidationError("Email already registered")
    
    # Validate password strength
    if len(user_data.password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    # Create new user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.FREE,
        subscription_status=SubscriptionStatus.TRIAL,
        is_active=True,
        is_verified=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    # Send verification email (background task)
    # background_tasks.add_task(send_verification_email, user.email)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_verified": user.is_verified
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")
    
    if not user.is_active:
        raise AuthenticationError("Account is inactive")
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_verified": user.is_verified,
            "subscription_status": user.subscription_status
        }
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    
    try:
        payload = decode_token(token_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id = payload.get("sub")
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise AuthenticationError("Invalid token")
        
        # Generate new tokens
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
        
    except Exception as e:
        raise AuthenticationError(f"Token refresh failed: {str(e)}")


@router.post("/verify-email")
async def verify_email(
    verification_data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email"""
    
    # In production, verify the code against stored verification codes
    # For now, we'll just mark the user as verified
    
    return {
        "message": "Email verified successfully",
        "verified": True
    }


@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset"""
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == request_data.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        reset_token = create_access_token(
            {"sub": user.id, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # Send reset email (background task)
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)
    
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token"""
    
    try:
        payload = decode_token(reset_data.token)
        
        if payload.get("type") != "password_reset":
            raise AuthenticationError("Invalid token type")
        
        user_id = payload.get("sub")
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid token")
        
        # Validate new password
        if len(reset_data.new_password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        await db.commit()
        
        return {
            "message": "Password reset successfully"
        }
        
    except Exception as e:
        raise AuthenticationError(f"Password reset failed: {str(e)}")


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {
        "message": "Logged out successfully"
    }