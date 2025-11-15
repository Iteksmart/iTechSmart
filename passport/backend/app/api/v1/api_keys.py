"""
API key management endpoints.
"""
from typing import Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...db.database import get_db
from ...models.user import User, APIKey
from ...schemas.user import APIKeyCreate, APIKeyResponse, APIKeyList
from ...core.security import generate_api_key, hash_api_key
from ...api.deps import get_current_user
import json

router = APIRouter()


@router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new API key."""
    
    # Generate API key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    key_prefix = api_key[:10]
    
    # Calculate expiration
    expires_at = None
    if api_key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)
    
    # Create API key
    new_api_key = APIKey(
        user_id=current_user.id,
        name=api_key_data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=json.dumps(api_key_data.scopes),
        expires_at=expires_at
    )
    
    db.add(new_api_key)
    await db.commit()
    await db.refresh(new_api_key)
    
    # Return with full key (only time it's shown)
    return {
        "id": new_api_key.id,
        "name": new_api_key.name,
        "key": api_key,  # Full key only returned on creation
        "key_prefix": new_api_key.key_prefix,
        "scopes": json.loads(new_api_key.scopes),
        "is_active": new_api_key.is_active,
        "expires_at": new_api_key.expires_at,
        "created_at": new_api_key.created_at
    }


@router.get("/", response_model=List[APIKeyList])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List user's API keys."""
    
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == current_user.id)
    )
    api_keys = result.scalars().all()
    
    return [
        {
            "id": key.id,
            "name": key.name,
            "key_prefix": key.key_prefix,
            "scopes": json.loads(key.scopes),
            "is_active": key.is_active,
            "expires_at": key.expires_at,
            "last_used_at": key.last_used_at,
            "usage_count": key.usage_count,
            "created_at": key.created_at
        }
        for key in api_keys
    ]


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete an API key."""
    
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == api_key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    await db.delete(api_key)
    await db.commit()
    
    return {"message": "API key deleted successfully"}


@router.put("/{api_key_id}/toggle")
async def toggle_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Toggle API key active status."""
    
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == api_key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = not api_key.is_active
    await db.commit()
    
    return {
        "message": f"API key {'activated' if api_key.is_active else 'deactivated'} successfully",
        "is_active": api_key.is_active
    }