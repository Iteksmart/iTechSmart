"""
Emergency access endpoints.
"""

from typing import Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...db.database import get_db
from ...models.user import User
from ...models.password import EmergencyAccess
from ...schemas.password import EmergencyAccessCreate, EmergencyAccessResponse
from ...api.deps import get_current_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_emergency_access(
    emergency_data: EmergencyAccessCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Grant emergency access to a trusted contact."""

    # Find grantee user
    result = await db.execute(
        select(User).where(User.email == emergency_data.grantee_email)
    )
    grantee_user = result.scalar_one_or_none()

    if not grantee_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if grantee_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot grant emergency access to yourself",
        )

    # Check if already exists
    result = await db.execute(
        select(EmergencyAccess).where(
            EmergencyAccess.grantor_id == current_user.id,
            EmergencyAccess.grantee_id == grantee_user.id,
            EmergencyAccess.status != "rejected",
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emergency access already granted to this user",
        )

    # Create emergency access
    emergency_access = EmergencyAccess(
        grantor_id=current_user.id,
        grantee_id=grantee_user.id,
        delay_hours=emergency_data.delay_hours,
        access_level=emergency_data.access_level,
        status="active",
    )

    db.add(emergency_access)
    await db.commit()
    await db.refresh(emergency_access)

    # TODO: Send email notification

    return {
        "message": "Emergency access granted successfully",
        "grantee_email": emergency_data.grantee_email,
    }


@router.get("/granted", response_model=List[EmergencyAccessResponse])
async def list_granted_access(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """List emergency access granted by current user."""

    result = await db.execute(
        select(EmergencyAccess, User)
        .join(User, EmergencyAccess.grantee_id == User.id)
        .where(EmergencyAccess.grantor_id == current_user.id)
    )

    accesses = []
    for emergency_access, user in result:
        accesses.append(
            {
                "id": emergency_access.id,
                "grantor_email": current_user.email,
                "grantee_email": user.email,
                "delay_hours": emergency_access.delay_hours,
                "access_level": emergency_access.access_level,
                "status": emergency_access.status,
                "created_at": emergency_access.created_at,
            }
        )

    return accesses


@router.get("/received", response_model=List[EmergencyAccessResponse])
async def list_received_access(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """List emergency access received by current user."""

    result = await db.execute(
        select(EmergencyAccess, User)
        .join(User, EmergencyAccess.grantor_id == User.id)
        .where(EmergencyAccess.grantee_id == current_user.id)
    )

    accesses = []
    for emergency_access, user in result:
        accesses.append(
            {
                "id": emergency_access.id,
                "grantor_email": user.email,
                "grantee_email": current_user.email,
                "delay_hours": emergency_access.delay_hours,
                "access_level": emergency_access.access_level,
                "status": emergency_access.status,
                "created_at": emergency_access.created_at,
            }
        )

    return accesses


@router.post("/{access_id}/request")
async def request_emergency_access(
    access_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Request emergency access to a vault."""

    result = await db.execute(
        select(EmergencyAccess).where(
            EmergencyAccess.id == access_id,
            EmergencyAccess.grantee_id == current_user.id,
            EmergencyAccess.status == "active",
        )
    )
    emergency_access = result.scalar_one_or_none()

    if not emergency_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Emergency access not found"
        )

    # Update status
    emergency_access.status = "requested"
    emergency_access.requested_at = datetime.utcnow()

    await db.commit()

    # TODO: Send email notification to grantor

    return {
        "message": "Emergency access requested successfully",
        "available_at": emergency_access.requested_at
        + timedelta(hours=emergency_access.delay_hours),
    }


@router.post("/{access_id}/approve")
async def approve_emergency_access(
    access_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Approve emergency access request."""

    result = await db.execute(
        select(EmergencyAccess).where(
            EmergencyAccess.id == access_id,
            EmergencyAccess.grantor_id == current_user.id,
            EmergencyAccess.status == "requested",
        )
    )
    emergency_access = result.scalar_one_or_none()

    if not emergency_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency access request not found",
        )

    # Update status
    emergency_access.status = "granted"
    emergency_access.granted_at = datetime.utcnow()

    await db.commit()

    # TODO: Send email notification to grantee

    return {"message": "Emergency access approved successfully"}


@router.post("/{access_id}/reject")
async def reject_emergency_access(
    access_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Reject emergency access request."""

    result = await db.execute(
        select(EmergencyAccess).where(
            EmergencyAccess.id == access_id,
            EmergencyAccess.grantor_id == current_user.id,
            EmergencyAccess.status == "requested",
        )
    )
    emergency_access = result.scalar_one_or_none()

    if not emergency_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency access request not found",
        )

    # Update status
    emergency_access.status = "rejected"
    emergency_access.rejected_at = datetime.utcnow()

    await db.commit()

    # TODO: Send email notification to grantee

    return {"message": "Emergency access rejected successfully"}


@router.delete("/{access_id}")
async def revoke_emergency_access(
    access_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Revoke emergency access."""

    result = await db.execute(
        select(EmergencyAccess).where(
            EmergencyAccess.id == access_id,
            EmergencyAccess.grantor_id == current_user.id,
        )
    )
    emergency_access = result.scalar_one_or_none()

    if not emergency_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Emergency access not found"
        )

    await db.delete(emergency_access)
    await db.commit()

    return {"message": "Emergency access revoked successfully"}
