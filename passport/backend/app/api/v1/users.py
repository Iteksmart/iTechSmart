"""
User management endpoints.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ...db.database import get_db
from ...models.user import User
from ...models.password import Password
from ...schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordChange,
    MasterPasswordChange,
    UserStats,
)
from ...core.security import verify_password, get_password_hash
from ...api.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update current user information."""

    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    if user_data.emergency_contact_email is not None:
        current_user.emergency_contact_email = user_data.emergency_contact_email
    if user_data.emergency_access_delay_hours is not None:
        current_user.emergency_access_delay_hours = (
            user_data.emergency_access_delay_hours
        )

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Change user password."""

    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)

    await db.commit()

    return {"message": "Password changed successfully"}


@router.post("/me/change-master-password")
async def change_master_password(
    password_data: MasterPasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Change master password."""

    # Verify current master password
    if not verify_password(
        password_data.current_master_password, current_user.master_password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current master password",
        )

    # Update master password
    current_user.master_password_hash = get_password_hash(
        password_data.new_master_password
    )

    await db.commit()

    return {"message": "Master password changed successfully"}


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user statistics."""

    # Count passwords
    total_passwords_result = await db.execute(
        select(func.count(Password.id)).where(
            Password.user_id == current_user.id, Password.is_deleted == False
        )
    )
    total_passwords = total_passwords_result.scalar() or 0

    # Count weak passwords
    weak_passwords_result = await db.execute(
        select(func.count(Password.id)).where(
            Password.user_id == current_user.id,
            Password.is_deleted == False,
            Password.password_strength == "weak",
        )
    )
    weak_passwords = weak_passwords_result.scalar() or 0

    # Count compromised passwords
    compromised_passwords_result = await db.execute(
        select(func.count(Password.id)).where(
            Password.user_id == current_user.id,
            Password.is_deleted == False,
            Password.is_compromised == True,
        )
    )
    compromised_passwords = compromised_passwords_result.scalar() or 0

    # Count shared passwords
    shared_passwords_result = await db.execute(
        select(func.count(Password.id)).where(
            Password.user_id == current_user.id,
            Password.is_deleted == False,
            Password.is_shared == True,
        )
    )
    shared_passwords = shared_passwords_result.scalar() or 0

    # Count folders
    folders_result = await db.execute(
        select(func.count(func.distinct(Password.folder))).where(
            Password.user_id == current_user.id,
            Password.is_deleted == False,
            Password.folder.isnot(None),
        )
    )
    folders = folders_result.scalar() or 0

    # Calculate account age
    from datetime import datetime

    account_age_days = (datetime.utcnow() - current_user.created_at).days

    # Calculate security score (0-100)
    security_score = 100
    if weak_passwords > 0:
        security_score -= min(weak_passwords * 10, 30)
    if compromised_passwords > 0:
        security_score -= min(compromised_passwords * 20, 40)
    if not current_user.totp_enabled:
        security_score -= 10
    if not current_user.is_verified:
        security_score -= 10

    security_score = max(0, security_score)

    return {
        "total_passwords": total_passwords,
        "weak_passwords": weak_passwords,
        "compromised_passwords": compromised_passwords,
        "shared_passwords": shared_passwords,
        "folders": folders,
        "last_login": current_user.last_login_at,
        "account_age_days": account_age_days,
        "security_score": security_score,
    }


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete user account."""

    # Soft delete user
    current_user.is_active = False

    # Soft delete all passwords
    result = await db.execute(
        select(Password).where(
            Password.user_id == current_user.id, Password.is_deleted == False
        )
    )
    passwords = result.scalars().all()

    for password in passwords:
        password.is_deleted = True
        password.deleted_at = func.now()

    await db.commit()

    return {"message": "Account deleted successfully"}
