"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.core.security import get_password_hash, generate_api_key
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User, APIKey
from app.core.exceptions import ValidationError, NotFoundError

router = APIRouter()


# Schemas
class UserProfile(BaseModel):
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    role: str
    subscription_status: str
    is_verified: bool
    proofs_created_this_month: int
    storage_used_mb: int
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str
    key_prefix: str
    created_at: str
    
    class Config:
        from_attributes = True


# Endpoints
@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    
    # Update fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.username is not None:
        # Check if username is taken
        result = await db.execute(
            select(User).where(User.username == user_update.username, User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise ValidationError("Username already taken")
        current_user.username = user_update.username
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.website is not None:
        current_user.website = user_update.website
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    
    from app.core.security import verify_password
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise ValidationError("Current password is incorrect")
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me/api-keys")
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's API keys"""
    
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == current_user.id)
    )
    api_keys = result.scalars().all()
    
    return {
        "api_keys": [
            {
                "id": key.id,
                "name": key.name,
                "key_prefix": key.key_prefix,
                "is_active": key.is_active,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                "created_at": key.created_at.isoformat()
            }
            for key in api_keys
        ]
    }


@router.post("/me/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new API key"""
    
    # Generate API key
    key, prefix = generate_api_key()
    
    # Create API key record
    api_key = APIKey(
        user_id=current_user.id,
        name=key_data.name,
        key=key,
        key_prefix=prefix
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=key,  # Only returned once
        key_prefix=prefix,
        created_at=api_key.created_at.isoformat()
    )


@router.delete("/me/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete API key"""
    
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise NotFoundError("API key not found")
    
    await db.delete(api_key)
    await db.commit()
    
    return {"message": "API key deleted successfully"}


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics"""
    
    from app.models.proof import Proof
    from sqlalchemy import func
    
    # Get proof count
    proof_count = await db.execute(
        select(func.count(Proof.id)).where(Proof.user_id == current_user.id)
    )
    total_proofs = proof_count.scalar()
    
    # Get verification count
    verification_count = await db.execute(
        select(func.sum(Proof.verification_count)).where(Proof.user_id == current_user.id)
    )
    total_verifications = verification_count.scalar() or 0
    
    return {
        "total_proofs": total_proofs,
        "proofs_this_month": current_user.proofs_created_this_month,
        "total_verifications": total_verifications,
        "storage_used_mb": current_user.storage_used_mb,
        "api_calls_today": current_user.api_calls_today,
        "role": current_user.role.value,
        "subscription_status": current_user.subscription_status.value
    }


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account"""
    
    # TODO: Delete all user data (proofs, files, etc.)
    
    await db.delete(current_user)
    await db.commit()
    
    return {"message": "Account deleted successfully"}