"""
iTechSmart Citadel - Compliance API
Compliance management and policy enforcement endpoints

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models import CompliancePolicy, ComplianceCheck
from engine import CitadelEngine
from config import COMPLIANCE_FRAMEWORKS_CONFIG

router = APIRouter()


# Pydantic models
class CompliancePolicyCreate(BaseModel):
    name: str
    framework: str
    description: str
    requirements: List[str]


class CompliancePolicyResponse(BaseModel):
    id: int
    name: str
    framework: str
    description: str
    requirements: List[str]
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceCheckResponse(BaseModel):
    id: int
    policy_id: int
    check_name: str
    status: str
    score: float
    findings: List[dict]
    checked_at: datetime

    class Config:
        from_attributes = True


@router.post("/policies", response_model=CompliancePolicyResponse)
async def create_compliance_policy(
    policy: CompliancePolicyCreate, db: Session = Depends(get_db)
):
    """Create a compliance policy"""
    engine = CitadelEngine(db)
    new_policy = engine.create_compliance_policy(
        name=policy.name,
        framework=policy.framework,
        description=policy.description,
        requirements=policy.requirements,
    )
    return new_policy


@router.get("/policies", response_model=List[CompliancePolicyResponse])
async def list_compliance_policies(
    framework: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List compliance policies"""
    query = db.query(CompliancePolicy)

    if framework:
        query = query.filter(CompliancePolicy.framework == framework)
    if enabled is not None:
        query = query.filter(CompliancePolicy.enabled == enabled)

    policies = query.order_by(CompliancePolicy.created_at.desc()).all()
    return policies


@router.get("/policies/{policy_id}", response_model=CompliancePolicyResponse)
async def get_compliance_policy(policy_id: int, db: Session = Depends(get_db)):
    """Get compliance policy by ID"""
    policy = db.query(CompliancePolicy).filter(CompliancePolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Compliance policy not found")
    return policy


@router.post("/policies/{policy_id}/check")
async def run_compliance_check(policy_id: int, db: Session = Depends(get_db)):
    """Run compliance checks for a policy"""
    engine = CitadelEngine(db)
    try:
        checks = engine.run_compliance_check(policy_id)
        return {
            "policy_id": policy_id,
            "checks_completed": len(checks),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/policies/{policy_id}/checks", response_model=List[ComplianceCheckResponse]
)
async def get_policy_checks(policy_id: int, db: Session = Depends(get_db)):
    """Get compliance checks for a policy"""
    checks = (
        db.query(ComplianceCheck)
        .filter(ComplianceCheck.policy_id == policy_id)
        .order_by(ComplianceCheck.checked_at.desc())
        .all()
    )
    return checks


@router.get("/frameworks")
async def list_frameworks():
    """List available compliance frameworks"""
    return {
        "frameworks": list(COMPLIANCE_FRAMEWORKS_CONFIG.keys()),
        "details": COMPLIANCE_FRAMEWORKS_CONFIG,
    }


@router.get("/frameworks/{framework}/score")
async def get_framework_score(framework: str, db: Session = Depends(get_db)):
    """Get compliance score for a framework"""
    engine = CitadelEngine(db)
    score = engine.get_compliance_score(framework)
    return {
        "framework": framework,
        "score": score,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stats/summary")
async def get_compliance_stats(db: Session = Depends(get_db)):
    """Get compliance statistics"""
    total_policies = db.query(CompliancePolicy).count()
    enabled_policies = (
        db.query(CompliancePolicy).filter(CompliancePolicy.enabled == True).count()
    )
    total_checks = db.query(ComplianceCheck).count()
    passed_checks = (
        db.query(ComplianceCheck).filter(ComplianceCheck.status == "passed").count()
    )

    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    return {
        "total_policies": total_policies,
        "enabled_policies": enabled_policies,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "pass_rate": round(pass_rate, 2),
    }
