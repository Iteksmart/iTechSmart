"""
CRM Integration API Endpoints
REST API endpoints for managing CRM integrations and data synchronization
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging

from ..crm_integrations.manager import CRMIntegrationManager
from ..crm_integrations.base_crm import CRMContact
from ...cdp_engine import CDPEngine

logger = logging.getLogger(__name__)


# Pydantic models for API
class CRMConfig(BaseModel):
    salesforce: Optional[Dict[str, Any]] = None
    hubspot: Optional[Dict[str, Any]] = None
    marketo: Optional[Dict[str, Any]] = None


class ContactCreate(BaseModel):
    email: str = Field(..., description="Contact email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    lead_score: Optional[int] = Field(None, description="Lead score")
    source: Optional[str] = Field(None, description="Lead source")


class ContactUpdate(BaseModel):
    email: Optional[str] = Field(None, description="Contact email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    lead_score: Optional[int] = Field(None, description="Lead score")
    source: Optional[str] = Field(None, description="Lead source")


class SyncRequest(BaseModel):
    incremental: bool = Field(True, description="Perform incremental sync")
    force_full: bool = Field(False, description="Force full sync")


# Router
router = APIRouter(prefix="/api/v1/crm", tags=["CRM Integration"])

# Global CDP engine instance (will be injected)
cdp_engine: CDPEngine = None


def set_cdp_engine(engine: CDPEngine):
    """Set the CDP engine instance"""
    global cdp_engine
    cdp_engine = engine


# API Endpoints


@router.post("/initialize", summary="Initialize CRM integrations")
async def initialize_crm_integrations(config: CRMConfig):
    """
    Initialize CRM integrations with provided configuration

    - **salesforce**: Salesforce configuration
    - **hubspot**: HubSpot configuration
    - **marketo**: Marketo configuration
    """
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        crm_configs = config.dict(exclude_unset=True)
        await cdp_engine.initialize_crm_integrations(crm_configs)

        return {
            "status": "success",
            "message": "CRM integrations initialized successfully",
            "configured_crms": list(crm_configs.keys()),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to initialize CRM integrations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize CRM integrations: {str(e)}"
        )


@router.get("/status", summary="Get CRM integration status")
async def get_crm_status():
    """Get current status of all CRM integrations"""
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        status = await cdp_engine.get_crm_sync_status()
        connections = await cdp_engine.test_crm_connections()

        return {
            "status": "success",
            "sync_status": status,
            "connection_status": connections,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get CRM status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get CRM status: {str(e)}"
        )


@router.post("/sync", summary="Sync CRM data")
async def sync_crm_data(
    background_tasks: BackgroundTasks, sync_request: SyncRequest = SyncRequest()
):
    """
    Trigger CRM data synchronization

    - **incremental**: Perform incremental sync (default: true)
    - **force_full**: Force full sync (default: false)
    """
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        # Start sync in background
        background_tasks.add_task(
            cdp_engine.sync_crm_data, incremental=not sync_request.force_full
        )

        return {
            "status": "started",
            "message": "CRM sync started in background",
            "sync_type": "incremental" if not sync_request.force_full else "full",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to start CRM sync: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start CRM sync: {str(e)}"
        )


@router.get("/contacts", summary="Get unified contacts")
async def get_contacts(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of contacts to return"
    ),
    offset: int = Query(0, ge=0, description="Number of contacts to skip"),
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    email: Optional[str] = Query(None, description="Filter by email"),
    company: Optional[str] = Query(None, description="Filter by company"),
):
    """
    Get unified contacts from all CRM systems

    - **limit**: Maximum number of contacts to return
    - **offset**: Number of contacts to skip
    - **source_system**: Filter by CRM system (salesforce, hubspot, marketo)
    - **email**: Filter by email address
    - **company**: Filter by company name
    """
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        # Build filters
        filters = {}
        if source_system:
            filters["source_system"] = source_system
        if email:
            filters["email"] = email
        if company:
            filters["company"] = company

        contacts = await cdp_engine.get_crm_contacts(filters)

        # Apply pagination
        total = len(contacts)
        paginated_contacts = contacts[offset : offset + limit]

        return {
            "status": "success",
            "contacts": paginated_contacts,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get contacts: {str(e)}")


@router.post("/contacts", summary="Create contact in all CRMs")
async def create_contact(contact_data: ContactCreate):
    """
    Create a new contact in all configured CRM systems

    - **email**: Contact email address (required)
    - **first_name**: First name (required)
    - **last_name**: Last name (required)
    - **phone**: Phone number (optional)
    - **company**: Company name (optional)
    - **title**: Job title (optional)
    - **lead_score**: Lead score (optional)
    - **source**: Lead source (optional)
    """
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        contact = CRMContact(
            id="",  # Will be generated by CRM
            email=contact_data.email,
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            phone=contact_data.phone,
            company=contact_data.company,
            title=contact_data.title,
            lead_score=contact_data.lead_score,
            source=contact_data.source,
        )

        result = await cdp_engine.create_crm_contact(contact)

        return {
            "status": "success",
            "message": "Contact created successfully",
            "contact": {
                "email": contact_data.email,
                "name": f"{contact_data.first_name} {contact_data.last_name}",
            },
            "crm_results": result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to create contact: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create contact: {str(e)}"
        )


@router.put("/contacts/{contact_id}", summary="Update contact in all CRMs")
async def update_contact(contact_id: str, update_data: ContactUpdate):
    """
    Update an existing contact in all CRM systems

    - **contact_id**: Contact ID to update
    - **email**: Updated email address (optional)
    - **first_name**: Updated first name (optional)
    - **last_name**: Updated last name (optional)
    - **phone**: Updated phone number (optional)
    - **company**: Updated company name (optional)
    - **title**: Updated job title (optional)
    - **lead_score**: Updated lead score (optional)
    - **source**: Updated lead source (optional)
    """
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        # Build update data (only include non-None fields)
        update_fields = update_data.dict(exclude_unset=True)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        result = await cdp_engine.update_crm_contact(contact_id, update_fields)

        return {
            "status": "success",
            "message": "Contact updated successfully",
            "contact_id": contact_id,
            "updated_fields": list(update_fields.keys()),
            "crm_results": result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to update contact: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update contact: {str(e)}"
        )


@router.get("/health", summary="Health check for CRM integrations")
async def health_check():
    """Health check endpoint for CRM integrations"""
    try:
        if not cdp_engine:
            return {
                "status": "unhealthy",
                "message": "CDP engine not initialized",
                "timestamp": datetime.now().isoformat(),
            }

        # Test CRM connections
        connections = await cdp_engine.test_crm_connections()
        all_connected = all(connections.values())

        return {
            "status": "healthy" if all_connected else "degraded",
            "connections": connections,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.delete("/contacts/{contact_id}", summary="Delete contact from CRMs")
async def delete_contact(contact_id: str):
    """
    Delete a contact from all CRM systems
    Note: This is a destructive operation and cannot be undone

    - **contact_id**: Contact ID to delete
    """
    if not cdp_engine:
        raise HTTPException(status_code=500, detail="CDP engine not initialized")

    try:
        # Note: This would need to be implemented in the CRM connectors
        # For now, return a not implemented response
        raise HTTPException(
            status_code=501, detail="Contact deletion is not yet implemented"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete contact: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete contact: {str(e)}"
        )
