"""
iTechSmart Supreme Plus - Integrations API
Endpoints for integration management

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models import Integration
from engine import SupremePlusEngine
from config import INTEGRATION_TYPES

router = APIRouter()


# Pydantic models
class IntegrationCreate(BaseModel):
    name: str
    integration_type: str
    config: dict
    enabled: bool = True


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[dict] = None
    enabled: Optional[bool] = None


class IntegrationResponse(BaseModel):
    id: int
    name: str
    integration_type: str
    config: dict
    enabled: bool
    last_sync: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    integration: IntegrationCreate, db: Session = Depends(get_db)
):
    """Create a new integration"""
    if integration.integration_type not in INTEGRATION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid integration type. Must be one of: {', '.join(INTEGRATION_TYPES)}",
        )

    engine = SupremePlusEngine(db)
    new_integration = engine.create_integration(
        name=integration.name,
        integration_type=integration.integration_type,
        config=integration.config,
        enabled=integration.enabled,
    )
    return new_integration


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    integration_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List integrations with optional filters"""
    query = db.query(Integration)

    if integration_type:
        query = query.filter(Integration.integration_type == integration_type)
    if enabled is not None:
        query = query.filter(Integration.enabled == enabled)

    integrations = (
        query.order_by(Integration.created_at.desc()).offset(offset).limit(limit).all()
    )
    return integrations


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(integration_id: int, db: Session = Depends(get_db)):
    """Get integration by ID"""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_update: IntegrationUpdate,
    db: Session = Depends(get_db),
):
    """Update an integration"""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    update_data = integration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)

    db.commit()
    db.refresh(integration)
    return integration


@router.delete("/{integration_id}")
async def delete_integration(integration_id: int, db: Session = Depends(get_db)):
    """Delete an integration"""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    db.delete(integration)
    db.commit()
    return {"message": "Integration deleted successfully"}


@router.post("/{integration_id}/test")
async def test_integration(integration_id: int, db: Session = Depends(get_db)):
    """Test an integration connection"""
    engine = SupremePlusEngine(db)
    try:
        result = engine.test_integration(integration_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{integration_id}/sync")
async def sync_integration(integration_id: int, db: Session = Depends(get_db)):
    """Trigger a sync for an integration"""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if not integration.enabled:
        raise HTTPException(status_code=400, detail="Integration is disabled")

    # Update last sync time
    integration.last_sync = datetime.utcnow()
    db.commit()

    return {
        "message": "Sync triggered successfully",
        "integration_id": integration_id,
        "last_sync": integration.last_sync,
    }


@router.get("/types/list")
async def list_integration_types():
    """List available integration types"""
    return {
        "types": INTEGRATION_TYPES,
        "descriptions": {
            "prometheus": "Prometheus monitoring system",
            "wazuh": "Wazuh security platform",
            "grafana": "Grafana visualization",
            "elasticsearch": "Elasticsearch log aggregation",
            "splunk": "Splunk SIEM",
            "datadog": "Datadog monitoring",
            "new_relic": "New Relic APM",
            "pagerduty": "PagerDuty incident management",
            "slack": "Slack notifications",
            "webhook": "Generic webhook integration",
        },
    }
