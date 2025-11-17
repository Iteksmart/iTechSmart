"""
Third-party integration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from ...config import settings

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, Integration
from app.core.exceptions import IntegrationError

router = APIRouter()


# Schemas
class IntegrationConnect(BaseModel):
    provider: str
    access_token: Optional[str] = None


class IntegrationResponse(BaseModel):
    id: str
    provider: str
    is_active: bool
    connected_at: str


# Endpoints
@router.get("/")
async def get_integrations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's integrations"""

    from sqlalchemy import select

    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    integrations = result.scalars().all()

    return {
        "integrations": [
            {
                "id": integration.id,
                "provider": integration.provider,
                "is_active": integration.is_active,
                "connected_at": integration.created_at.isoformat(),
            }
            for integration in integrations
        ]
    }


@router.get("/available")
async def get_available_integrations():
    """Get available integrations"""

    return {
        "integrations": [
            {
                "provider": "google_drive",
                "name": "Google Drive",
                "description": "Store and verify files from Google Drive",
                "icon": "https://cdn.prooflink.ai/icons/google-drive.svg",
            },
            {
                "provider": "dropbox",
                "name": "Dropbox",
                "description": "Store and verify files from Dropbox",
                "icon": "https://cdn.prooflink.ai/icons/dropbox.svg",
            },
            {
                "provider": "slack",
                "name": "Slack",
                "description": "Share proofs in Slack channels",
                "icon": "https://cdn.prooflink.ai/icons/slack.svg",
            },
            {
                "provider": "gmail",
                "name": "Gmail",
                "description": "Verify emails and attachments",
                "icon": "https://cdn.prooflink.ai/icons/gmail.svg",
            },
            {
                "provider": "outlook",
                "name": "Outlook",
                "description": "Verify emails and attachments",
                "icon": "https://cdn.prooflink.ai/icons/outlook.svg",
            },
        ]
    }


@router.post("/connect/{provider}")
async def connect_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect to a third-party service"""

    # TODO: Implement OAuth flow for each provider

    if provider == "google_drive":
        # Return OAuth URL
        return {
            "auth_url": f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&response_type=code&scope=https://www.googleapis.com/auth/drive.readonly"
        }

    raise IntegrationError(f"Provider {provider} not supported")


@router.get("/{provider}/callback")
async def integration_callback(
    provider: str,
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Handle OAuth callback"""

    # TODO: Exchange code for access token
    # TODO: Store integration

    return {"message": "Integration connected successfully"}


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect integration"""

    from sqlalchemy import select, and_

    result = await db.execute(
        select(Integration).where(
            and_(
                Integration.id == integration_id, Integration.user_id == current_user.id
            )
        )
    )
    integration = result.scalar_one_or_none()

    if not integration:
        raise IntegrationError("Integration not found")

    await db.delete(integration)
    await db.commit()

    return {"message": "Integration disconnected successfully"}
