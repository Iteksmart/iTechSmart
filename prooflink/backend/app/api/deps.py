"""
API dependencies
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from sqlalchemy import select

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise AuthenticationError("Invalid authentication credentials")

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        return user

    except JWTError:
        raise AuthenticationError("Invalid authentication credentials")


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current verified user"""
    if not current_user.is_verified:
        raise AuthorizationError("Email verification required")
    return current_user


async def get_current_premium_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current premium user"""
    if current_user.role not in [
        UserRole.PREMIUM,
        UserRole.LIFETIME,
        UserRole.ORGANIZATION,
        UserRole.ADMIN,
    ]:
        raise AuthorizationError("Premium subscription required")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current admin user"""
    if not current_user.is_superuser:
        raise AuthorizationError("Admin privileges required")
    return current_user


async def verify_api_key(
    x_api_key: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)
) -> User:
    """Verify API key and return associated user"""
    if not x_api_key:
        raise AuthenticationError("API key required")

    from app.models.user import APIKey

    # Get API key from database
    result = await db.execute(
        select(APIKey).where(APIKey.key == x_api_key, APIKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise AuthenticationError("Invalid API key")

    # Get associated user
    result = await db.execute(select(User).where(User.id == api_key.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError("Invalid API key")

    # Update last used timestamp
    from datetime import datetime

    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return user
