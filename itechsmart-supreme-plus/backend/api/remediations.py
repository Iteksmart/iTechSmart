"""
iTechSmart Supreme Plus - Remediations API
Endpoints for remediation management and execution

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models import Remediation, RemediationLog, RemediationTemplate
from engine import SupremePlusEngine
from config import REMEDIATION_TEMPLATES

router = APIRouter()

# Pydantic models
class RemediationCreate(BaseModel):
    incident_id: int
    action_type: str
    target_node_id: int
    parameters: Optional[dict] = None
    auto_execute: bool = False

class RemediationResponse(BaseModel):
    id: int
    incident_id: int
    action_type: str
    target_node_id: int
    parameters: dict
    status: str
    result: Optional[dict]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class RemediationLogResponse(BaseModel):
    id: int
    remediation_id: int
    action: str
    status: str
    output: str
    error: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=RemediationResponse)
async def create_remediation(remediation: RemediationCreate, db: Session = Depends(get_db)):
    """Create a new remediation"""
    engine = SupremePlusEngine(db)
    try:
        new_remediation = engine.create_remediation(
            incident_id=remediation.incident_id,
            action_type=remediation.action_type,
            target_node_id=remediation.target_node_id,
            parameters=remediation.parameters,
            auto_execute=remediation.auto_execute
        )
        return new_remediation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[RemediationResponse])
async def list_remediations(
    incident_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List remediations with optional filters"""
    query = db.query(Remediation)
    
    if incident_id:
        query = query.filter(Remediation.incident_id == incident_id)
    if status:
        query = query.filter(Remediation.status == status)
    
    remediations = query.order_by(Remediation.created_at.desc()).offset(offset).limit(limit).all()
    return remediations

@router.get("/{remediation_id}", response_model=RemediationResponse)
async def get_remediation(remediation_id: int, db: Session = Depends(get_db)):
    """Get remediation by ID"""
    remediation = db.query(Remediation).filter(Remediation.id == remediation_id).first()
    if not remediation:
        raise HTTPException(status_code=404, detail="Remediation not found")
    return remediation

@router.post("/{remediation_id}/execute")
async def execute_remediation(remediation_id: int, db: Session = Depends(get_db)):
    """Execute a remediation"""
    engine = SupremePlusEngine(db)
    try:
        result = engine.execute_remediation(remediation_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{remediation_id}/logs", response_model=List[RemediationLogResponse])
async def get_remediation_logs(remediation_id: int, db: Session = Depends(get_db)):
    """Get logs for a remediation"""
    logs = db.query(RemediationLog).filter(
        RemediationLog.remediation_id == remediation_id
    ).order_by(RemediationLog.timestamp.desc()).all()
    return logs

@router.get("/templates/list")
async def list_remediation_templates():
    """List available remediation templates"""
    templates = []
    for key, template in REMEDIATION_TEMPLATES.items():
        templates.append({
            "action_type": key,
            "name": template["name"],
            "description": template["description"],
            "commands": template["commands"]
        })
    return templates

@router.get("/templates/{action_type}")
async def get_remediation_template(action_type: str):
    """Get a specific remediation template"""
    template = REMEDIATION_TEMPLATES.get(action_type)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "action_type": action_type,
        "name": template["name"],
        "description": template["description"],
        "commands": template["commands"]
    }

@router.get("/stats/summary")
async def get_remediation_stats(db: Session = Depends(get_db)):
    """Get remediation statistics"""
    total = db.query(Remediation).count()
    pending = db.query(Remediation).filter(Remediation.status == "pending").count()
    in_progress = db.query(Remediation).filter(Remediation.status == "in_progress").count()
    success = db.query(Remediation).filter(Remediation.status == "success").count()
    failed = db.query(Remediation).filter(Remediation.status == "failed").count()
    
    success_rate = (success / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "success": success,
        "failed": failed,
        "success_rate": round(success_rate, 2)
    }