"""
Password management endpoints.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from ...db.database import get_db
from ...models.user import User
from ...models.password import Password, PasswordHistory, PasswordType, PasswordStrength
from ...schemas.password import (
    PasswordCreate,
    PasswordUpdate,
    PasswordResponse,
    PasswordListItem,
    PasswordGenerateRequest,
    PasswordGenerateResponse,
    PasswordStrengthRequest,
    PasswordStrengthResponse,
    BreachCheckRequest,
    BreachCheckResponse,
)
from ...core.security import (
    password_encryption,
    generate_password,
    analyze_password_strength,
)
from ...api.deps import get_current_user
import json
import httpx

router = APIRouter()


@router.post("/", response_model=PasswordResponse, status_code=status.HTTP_201_CREATED)
async def create_password(
    password_data: PasswordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new password."""

    # Encrypt password if provided
    encrypted_password = None
    password_strength = None
    password_score = None

    if password_data.password:
        encrypted_password = password_encryption.encrypt(password_data.password)

        # Analyze strength
        strength_analysis = analyze_password_strength(password_data.password)
        password_strength = PasswordStrength(strength_analysis["strength"])
        password_score = strength_analysis["score"]

    # Create password
    password = Password(
        user_id=current_user.id,
        name=password_data.name,
        type=password_data.type,
        folder=password_data.folder,
        username=password_data.username,
        encrypted_password=encrypted_password,
        url=password_data.url,
        card_number=(
            password_encryption.encrypt(password_data.card_number)
            if password_data.card_number
            else None
        ),
        card_holder=(
            password_encryption.encrypt(password_data.card_holder)
            if password_data.card_holder
            else None
        ),
        card_expiry=password_data.card_expiry,
        card_cvv=(
            password_encryption.encrypt(password_data.card_cvv)
            if password_data.card_cvv
            else None
        ),
        notes=(
            password_encryption.encrypt(password_data.notes)
            if password_data.notes
            else None
        ),
        tags=json.dumps(password_data.tags),
        custom_fields=json.dumps(password_data.custom_fields),
        password_strength=password_strength,
        password_score=password_score,
        auto_rotate=password_data.auto_rotate,
        rotation_days=password_data.rotation_days,
    )

    db.add(password)
    await db.commit()
    await db.refresh(password)

    # Decrypt for response
    return await _decrypt_password(password)


@router.get("/", response_model=List[PasswordListItem])
async def list_passwords(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    folder: Optional[str] = None,
    type: Optional[PasswordType] = None,
    is_favorite: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List user's passwords."""

    # Build query
    query = select(Password).where(
        Password.user_id == current_user.id, Password.is_deleted == False
    )

    # Apply filters
    if search:
        query = query.where(
            or_(
                Password.name.ilike(f"%{search}%"),
                Password.username.ilike(f"%{search}%"),
                Password.url.ilike(f"%{search}%"),
            )
        )

    if folder:
        query = query.where(Password.folder == folder)

    if type:
        query = query.where(Password.type == type)

    if is_favorite is not None:
        query = query.where(Password.is_favorite == is_favorite)

    # Order by updated_at desc
    query = query.order_by(Password.updated_at.desc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    passwords = result.scalars().all()

    return passwords


@router.get("/{password_id}", response_model=PasswordResponse)
async def get_password(
    password_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get a password by ID."""

    result = await db.execute(
        select(Password).where(
            Password.id == password_id,
            Password.user_id == current_user.id,
            Password.is_deleted == False,
        )
    )
    password = result.scalar_one_or_none()

    if not password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Password not found"
        )

    # Update usage
    password.last_used_at = func.now()
    password.usage_count += 1
    await db.commit()

    # Decrypt for response
    return await _decrypt_password(password)


@router.put("/{password_id}", response_model=PasswordResponse)
async def update_password(
    password_id: int,
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update a password."""

    result = await db.execute(
        select(Password).where(
            Password.id == password_id,
            Password.user_id == current_user.id,
            Password.is_deleted == False,
        )
    )
    password = result.scalar_one_or_none()

    if not password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Password not found"
        )

    # Save old password to history if password changed
    if password_data.password and password.encrypted_password:
        history = PasswordHistory(
            password_id=password.id,
            encrypted_password=password.encrypted_password,
            password_strength=password.password_strength,
            password_score=password.password_score,
        )
        db.add(history)

    # Update fields
    if password_data.name is not None:
        password.name = password_data.name
    if password_data.folder is not None:
        password.folder = password_data.folder
    if password_data.username is not None:
        password.username = password_data.username
    if password_data.password is not None:
        password.encrypted_password = password_encryption.encrypt(
            password_data.password
        )
        # Analyze strength
        strength_analysis = analyze_password_strength(password_data.password)
        password.password_strength = PasswordStrength(strength_analysis["strength"])
        password.password_score = strength_analysis["score"]
    if password_data.url is not None:
        password.url = password_data.url
    if password_data.card_number is not None:
        password.card_number = password_encryption.encrypt(password_data.card_number)
    if password_data.card_holder is not None:
        password.card_holder = password_encryption.encrypt(password_data.card_holder)
    if password_data.card_expiry is not None:
        password.card_expiry = password_data.card_expiry
    if password_data.card_cvv is not None:
        password.card_cvv = password_encryption.encrypt(password_data.card_cvv)
    if password_data.notes is not None:
        password.notes = password_encryption.encrypt(password_data.notes)
    if password_data.tags is not None:
        password.tags = json.dumps(password_data.tags)
    if password_data.custom_fields is not None:
        password.custom_fields = json.dumps(password_data.custom_fields)
    if password_data.auto_rotate is not None:
        password.auto_rotate = password_data.auto_rotate
    if password_data.rotation_days is not None:
        password.rotation_days = password_data.rotation_days
    if password_data.is_favorite is not None:
        password.is_favorite = password_data.is_favorite

    await db.commit()
    await db.refresh(password)

    # Decrypt for response
    return await _decrypt_password(password)


@router.delete("/{password_id}")
async def delete_password(
    password_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete a password (soft delete)."""

    result = await db.execute(
        select(Password).where(
            Password.id == password_id,
            Password.user_id == current_user.id,
            Password.is_deleted == False,
        )
    )
    password = result.scalar_one_or_none()

    if not password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Password not found"
        )

    # Soft delete
    password.is_deleted = True
    password.deleted_at = func.now()

    await db.commit()

    return {"message": "Password deleted successfully"}


@router.post("/generate", response_model=PasswordGenerateResponse)
async def generate_password_endpoint(
    request: PasswordGenerateRequest, current_user: User = Depends(get_current_user)
) -> Any:
    """Generate a secure password."""

    password = generate_password(
        length=request.length,
        use_uppercase=request.use_uppercase,
        use_lowercase=request.use_lowercase,
        use_digits=request.use_digits,
        use_symbols=request.use_symbols,
        exclude_ambiguous=request.exclude_ambiguous,
    )

    # Analyze strength
    strength_analysis = analyze_password_strength(password)

    return {
        "password": password,
        "strength": strength_analysis["strength"],
        "score": strength_analysis["score"],
    }


@router.post("/analyze", response_model=PasswordStrengthResponse)
async def analyze_password(
    request: PasswordStrengthRequest, current_user: User = Depends(get_current_user)
) -> Any:
    """Analyze password strength."""

    analysis = analyze_password_strength(request.password)
    return analysis


@router.post("/check-breach", response_model=BreachCheckResponse)
async def check_breach(
    request: BreachCheckRequest, current_user: User = Depends(get_current_user)
) -> Any:
    """Check if password has been compromised in data breaches."""

    # Use Have I Been Pwned API
    import hashlib

    # Hash password with SHA-1
    sha1_hash = hashlib.sha1(request.password.encode()).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                headers={"User-Agent": "iTechSmart-PassPort"},
            )

            if response.status_code == 200:
                hashes = response.text.split("\n")
                for hash_line in hashes:
                    hash_suffix, count = hash_line.split(":")
                    if hash_suffix == suffix:
                        return {
                            "is_compromised": True,
                            "breach_count": int(count),
                            "message": f"This password has been seen {count} times in data breaches. Please change it immediately.",
                        }

                return {
                    "is_compromised": False,
                    "breach_count": 0,
                    "message": "This password has not been found in any known data breaches.",
                }
    except Exception as e:
        # If API fails, return safe response
        return {
            "is_compromised": False,
            "breach_count": 0,
            "message": "Unable to check breach status at this time.",
        }


# Helper function to decrypt password
async def _decrypt_password(password: Password) -> dict:
    """Decrypt password fields for response."""
    return {
        "id": password.id,
        "name": password.name,
        "type": password.type,
        "folder": password.folder,
        "username": password.username,
        "password": (
            password_encryption.decrypt(password.encrypted_password)
            if password.encrypted_password
            else None
        ),
        "url": password.url,
        "card_number": (
            password_encryption.decrypt(password.card_number)
            if password.card_number
            else None
        ),
        "card_holder": (
            password_encryption.decrypt(password.card_holder)
            if password.card_holder
            else None
        ),
        "card_expiry": password.card_expiry,
        "card_cvv": (
            password_encryption.decrypt(password.card_cvv)
            if password.card_cvv
            else None
        ),
        "notes": (
            password_encryption.decrypt(password.notes) if password.notes else None
        ),
        "tags": json.loads(password.tags) if password.tags else [],
        "custom_fields": (
            json.loads(password.custom_fields) if password.custom_fields else {}
        ),
        "password_strength": password.password_strength,
        "password_score": password.password_score,
        "is_compromised": password.is_compromised,
        "breach_count": password.breach_count,
        "auto_rotate": password.auto_rotate,
        "rotation_days": password.rotation_days,
        "last_rotated_at": password.last_rotated_at,
        "next_rotation_at": password.next_rotation_at,
        "is_shared": password.is_shared,
        "is_favorite": password.is_favorite,
        "last_used_at": password.last_used_at,
        "usage_count": password.usage_count,
        "created_at": password.created_at,
        "updated_at": password.updated_at,
    }
