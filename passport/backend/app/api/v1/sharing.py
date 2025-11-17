"""
Password sharing endpoints.
"""

from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ...db.database import get_db
from ...models.user import User
from ...models.password import Password, SharedPassword
from ...schemas.password import PasswordShareRequest, SharedPasswordResponse
from ...api.deps import get_current_user

router = APIRouter()


@router.post("/{password_id}/share", status_code=status.HTTP_201_CREATED)
async def share_password(
    password_id: int,
    share_data: PasswordShareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Share a password with another user."""

    # Get password
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

    # Find user to share with
    result = await db.execute(select(User).where(User.email == share_data.email))
    shared_with_user = result.scalar_one_or_none()

    if not shared_with_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if shared_with_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share with yourself"
        )

    # Check if already shared
    result = await db.execute(
        select(SharedPassword).where(
            SharedPassword.password_id == password_id,
            SharedPassword.shared_with_id == shared_with_user.id,
            SharedPassword.is_revoked == False,
        )
    )
    existing_share = result.scalar_one_or_none()

    if existing_share:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password already shared with this user",
        )

    # Create share
    shared_password = SharedPassword(
        password_id=password_id,
        owner_id=current_user.id,
        shared_with_id=shared_with_user.id,
        can_view=share_data.can_view,
        can_edit=share_data.can_edit,
        can_share=share_data.can_share,
    )

    db.add(shared_password)

    # Mark password as shared
    password.is_shared = True

    await db.commit()
    await db.refresh(shared_password)

    # TODO: Send email notification

    return {"message": "Password shared successfully", "shared_with": share_data.email}


@router.get("/shared-by-me", response_model=List[SharedPasswordResponse])
async def list_shared_by_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """List passwords shared by current user."""

    result = await db.execute(
        select(SharedPassword, Password, User)
        .join(Password, SharedPassword.password_id == Password.id)
        .join(User, SharedPassword.shared_with_id == User.id)
        .where(
            SharedPassword.owner_id == current_user.id,
            SharedPassword.is_revoked == False,
        )
    )

    shares = []
    for shared_password, password, user in result:
        shares.append(
            {
                "id": shared_password.id,
                "password_id": password.id,
                "password_name": password.name,
                "owner_email": current_user.email,
                "shared_with_email": user.email,
                "can_view": shared_password.can_view,
                "can_edit": shared_password.can_edit,
                "can_share": shared_password.can_share,
                "is_accepted": shared_password.is_accepted,
                "created_at": shared_password.created_at,
            }
        )

    return shares


@router.get("/shared-with-me", response_model=List[SharedPasswordResponse])
async def list_shared_with_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """List passwords shared with current user."""

    result = await db.execute(
        select(SharedPassword, Password, User)
        .join(Password, SharedPassword.password_id == Password.id)
        .join(User, SharedPassword.owner_id == User.id)
        .where(
            SharedPassword.shared_with_id == current_user.id,
            SharedPassword.is_revoked == False,
        )
    )

    shares = []
    for shared_password, password, user in result:
        shares.append(
            {
                "id": shared_password.id,
                "password_id": password.id,
                "password_name": password.name,
                "owner_email": user.email,
                "shared_with_email": current_user.email,
                "can_view": shared_password.can_view,
                "can_edit": shared_password.can_edit,
                "can_share": shared_password.can_share,
                "is_accepted": shared_password.is_accepted,
                "created_at": shared_password.created_at,
            }
        )

    return shares


@router.post("/shared/{share_id}/accept")
async def accept_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Accept a shared password."""

    result = await db.execute(
        select(SharedPassword).where(
            SharedPassword.id == share_id,
            SharedPassword.shared_with_id == current_user.id,
            SharedPassword.is_revoked == False,
        )
    )
    shared_password = result.scalar_one_or_none()

    if not shared_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shared password not found"
        )

    shared_password.is_accepted = True
    shared_password.accepted_at = datetime.utcnow()

    await db.commit()

    return {"message": "Share accepted successfully"}


@router.post("/shared/{share_id}/reject")
async def reject_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Reject a shared password."""

    result = await db.execute(
        select(SharedPassword).where(
            SharedPassword.id == share_id,
            SharedPassword.shared_with_id == current_user.id,
            SharedPassword.is_revoked == False,
        )
    )
    shared_password = result.scalar_one_or_none()

    if not shared_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shared password not found"
        )

    shared_password.is_revoked = True
    shared_password.revoked_at = datetime.utcnow()

    await db.commit()

    return {"message": "Share rejected successfully"}


@router.delete("/shared/{share_id}")
async def revoke_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Revoke a shared password."""

    result = await db.execute(
        select(SharedPassword).where(
            SharedPassword.id == share_id,
            SharedPassword.owner_id == current_user.id,
            SharedPassword.is_revoked == False,
        )
    )
    shared_password = result.scalar_one_or_none()

    if not shared_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shared password not found"
        )

    shared_password.is_revoked = True
    shared_password.revoked_at = datetime.utcnow()

    await db.commit()

    return {"message": "Share revoked successfully"}
