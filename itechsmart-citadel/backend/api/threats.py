"""
iTechSmart Citadel - Threats API
Threat intelligence and vulnerability management endpoints

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models import ThreatIntelligence, Vulnerability
from engine import CitadelEngine

router = APIRouter()


# Pydantic models
class ThreatIndicatorCreate(BaseModel):
    threat_type: str
    indicator: str
    indicator_type: str
    confidence: float
    severity: str
    description: Optional[str] = None
    source: Optional[str] = None


class ThreatIndicatorResponse(BaseModel):
    id: int
    threat_type: str
    indicator: str
    indicator_type: str
    confidence: float
    severity: str
    description: Optional[str]
    source: Optional[str]
    first_seen: datetime
    last_seen: datetime
    is_active: bool

    class Config:
        from_attributes = True


class VulnerabilityCreate(BaseModel):
    asset_id: int
    title: str
    severity: str
    description: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None


class VulnerabilityResponse(BaseModel):
    id: int
    asset_id: int
    cve_id: Optional[str]
    title: str
    description: Optional[str]
    severity: str
    cvss_score: Optional[float]
    status: str
    discovered_at: datetime
    patched_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/indicators", response_model=ThreatIndicatorResponse)
async def add_threat_indicator(
    indicator: ThreatIndicatorCreate, db: Session = Depends(get_db)
):
    """Add a threat intelligence indicator"""
    engine = CitadelEngine(db)
    new_indicator = engine.add_threat_indicator(
        threat_type=indicator.threat_type,
        indicator=indicator.indicator,
        indicator_type=indicator.indicator_type,
        confidence=indicator.confidence,
        severity=indicator.severity,
        description=indicator.description,
        source=indicator.source,
    )
    return new_indicator


@router.get("/indicators", response_model=List[ThreatIndicatorResponse])
async def list_threat_indicators(
    threat_type: Optional[str] = None,
    indicator_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List threat intelligence indicators"""
    query = db.query(ThreatIntelligence)

    if threat_type:
        query = query.filter(ThreatIntelligence.threat_type == threat_type)
    if indicator_type:
        query = query.filter(ThreatIntelligence.indicator_type == indicator_type)
    if is_active is not None:
        query = query.filter(ThreatIntelligence.is_active == is_active)

    indicators = (
        query.order_by(ThreatIntelligence.last_seen.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return indicators


@router.get("/indicators/check/{indicator}")
async def check_threat_indicator(
    indicator: str, indicator_type: str, db: Session = Depends(get_db)
):
    """Check if an indicator is in threat intelligence database"""
    engine = CitadelEngine(db)
    threat = engine.check_threat_indicator(indicator, indicator_type)

    if threat:
        return {
            "found": True,
            "threat_type": threat.threat_type,
            "severity": threat.severity,
            "confidence": threat.confidence,
            "last_seen": threat.last_seen.isoformat(),
        }
    else:
        return {"found": False}


@router.post("/indicators/update-feeds")
async def update_threat_feeds(db: Session = Depends(get_db)):
    """Update threat intelligence feeds"""
    engine = CitadelEngine(db)
    result = engine.update_threat_feeds()
    return result


@router.post("/vulnerabilities", response_model=VulnerabilityResponse)
async def add_vulnerability(vuln: VulnerabilityCreate, db: Session = Depends(get_db)):
    """Add a vulnerability"""
    engine = CitadelEngine(db)
    new_vuln = engine.add_vulnerability(
        asset_id=vuln.asset_id,
        title=vuln.title,
        severity=vuln.severity,
        description=vuln.description,
        cve_id=vuln.cve_id,
        cvss_score=vuln.cvss_score,
    )
    return new_vuln


@router.get("/vulnerabilities", response_model=List[VulnerabilityResponse])
async def list_vulnerabilities(
    asset_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List vulnerabilities"""
    query = db.query(Vulnerability)

    if asset_id:
        query = query.filter(Vulnerability.asset_id == asset_id)
    if severity:
        query = query.filter(Vulnerability.severity == severity)
    if status:
        query = query.filter(Vulnerability.status == status)

    vulnerabilities = (
        query.order_by(Vulnerability.discovered_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return vulnerabilities


@router.post("/vulnerabilities/scan/{asset_id}")
async def scan_asset(asset_id: int, db: Session = Depends(get_db)):
    """Scan an asset for vulnerabilities"""
    engine = CitadelEngine(db)
    try:
        vulnerabilities = engine.scan_asset_vulnerabilities(asset_id)
        return {
            "asset_id": asset_id,
            "vulnerabilities_found": len(vulnerabilities),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats/summary")
async def get_threat_stats(db: Session = Depends(get_db)):
    """Get threat intelligence statistics"""
    total_indicators = db.query(ThreatIntelligence).count()
    active_indicators = (
        db.query(ThreatIntelligence)
        .filter(ThreatIntelligence.is_active == True)
        .count()
    )
    total_vulns = db.query(Vulnerability).count()
    open_vulns = db.query(Vulnerability).filter(Vulnerability.status == "open").count()
    critical_vulns = (
        db.query(Vulnerability)
        .filter(Vulnerability.severity == "critical", Vulnerability.status == "open")
        .count()
    )

    return {
        "threat_indicators": {"total": total_indicators, "active": active_indicators},
        "vulnerabilities": {
            "total": total_vulns,
            "open": open_vulns,
            "critical": critical_vulns,
        },
    }
