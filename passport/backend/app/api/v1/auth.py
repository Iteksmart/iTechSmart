"""
Authentication endpoints.
"""
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...db.database import get_db
from ...models.user import User, Session as UserSession
from ...schemas.user import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse,
    TOTPSetup,
    TOTPVerify
)
from ...core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    VaultEncryption,
    generate_totp_secret,
    verify_totp,
    get_totp_uri
)
from ...core.config import settings
import secrets

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user."""
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate vault salt
    vault_salt = VaultEncryption.generate_salt()
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        master_password_hash=get_password_hash(user_data.master_password),
        vault_salt=vault_salt.hex(),
        is_verified=False  # Require email verification
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # TODO: Send verification email
    
    return user


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login user."""
    
    # Get user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Please try again later."
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Verify 2FA if enabled
    if user.totp_enabled:
        if not user_data.totp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA code required"
            )
        
        if not verify_totp(user.totp_secret, user_data.totp_code):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )
    
    # Reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Create session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)
    
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token."""
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get session
    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        )
    )
    session = result.scalar_one_or_none()
    
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == session.user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Update session
    session.refresh_token = new_refresh_token
    session.last_used_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    await db.commit()
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Logout user."""
    
    # Deactivate session
    result = await db.execute(
        select(UserSession).where(UserSession.refresh_token == refresh_token)
    )
    session = result.scalar_one_or_none()
    
    if session:
        session.is_active = False
        await db.commit()
    
    return {"message": "Logged out successfully"}


@router.post("/2fa/setup", response_model=TOTPSetup)
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Setup 2FA for user."""
    
    # Generate TOTP secret
    secret = generate_totp_secret()
    
    # Save to user (but don't enable yet)
    current_user.totp_secret = secret
    await db.commit()
    
    # Generate QR code URI
    qr_uri = get_totp_uri(secret, current_user.email)
    
    return {
        "secret": secret,
        "qr_code_uri": qr_uri
    }


@router.post("/2fa/verify")
async def verify_2fa(
    data: TOTPVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Verify and enable 2FA."""
    
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not set up"
        )
    
    # Verify code
    if not verify_totp(current_user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    
    # Enable 2FA
    current_user.totp_enabled = True
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4) for _ in range(10)]
    current_user.backup_codes = ",".join(backup_codes)
    
    await db.commit()
    
    return {
        "message": "2FA enabled successfully",
        "backup_codes": backup_codes
    }


@router.post("/2fa/disable")
async def disable_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Disable 2FA."""
    
    current_user.totp_enabled = False
    current_user.totp_secret = None
    current_user.backup_codes = None
    
    await db.commit()
    
    return {"message": "2FA disabled successfully"}


# Import get_current_user
from ...api.deps import get_current_user