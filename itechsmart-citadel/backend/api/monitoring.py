"""
iTechSmart Citadel - Monitoring API
Infrastructure monitoring and network analysis endpoints

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models import InfrastructureAsset, NetworkFlow, BackupJob, SIEMAlert, EncryptionKey
from engine import CitadelEngine

router = APIRouter()

# Pydantic models
class AssetCreate(BaseModel):
    asset_type: str
    name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    environment: str = "production"
    criticality: str = "medium"
    os_type: Optional[str] = None
    os_version: Optional[str] = None

class AssetResponse(BaseModel):
    id: int
    asset_type: str
    name: str
    hostname: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]
    environment: str
    criticality: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class NetworkFlowCreate(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str
    bytes_sent: int = 0
    bytes_received: int = 0

class BackupJobCreate(BaseModel):
    backup_type: str
    source: str
    destination: str
    retention_days: int = 90

@router.post("/assets", response_model=AssetResponse)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """Create an infrastructure asset"""
    new_asset = InfrastructureAsset(
        asset_type=asset.asset_type,
        name=asset.name,
        hostname=asset.hostname,
        ip_address=asset.ip_address,
        location=asset.location,
        environment=asset.environment,
        criticality=asset.criticality,
        status="active",
        os_type=asset.os_type,
        os_version=asset.os_version,
        created_at=datetime.utcnow()
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.get("/assets", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[str] = None,
    environment: Optional[str] = None,
    criticality: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List infrastructure assets"""
    query = db.query(InfrastructureAsset)
    
    if asset_type:
        query = query.filter(InfrastructureAsset.asset_type == asset_type)
    if environment:
        query = query.filter(InfrastructureAsset.environment == environment)
    if criticality:
        query = query.filter(InfrastructureAsset.criticality == criticality)
    if status:
        query = query.filter(InfrastructureAsset.status == status)
    
    assets = query.order_by(InfrastructureAsset.created_at.desc()).offset(offset).limit(limit).all()
    return assets

@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get asset by ID"""
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/network-flows")
async def analyze_network_flow(flow: NetworkFlowCreate, db: Session = Depends(get_db)):
    """Analyze and record network flow"""
    engine = CitadelEngine(db)
    network_flow = engine.analyze_network_flow(
        source_ip=flow.source_ip,
        destination_ip=flow.destination_ip,
        protocol=flow.protocol,
        bytes_sent=flow.bytes_sent,
        bytes_received=flow.bytes_received
    )
    return {
        "flow_id": network_flow.id,
        "is_suspicious": network_flow.is_suspicious,
        "threat_score": network_flow.threat_score
    }

@router.get("/network-flows")
async def list_network_flows(
    source_ip: Optional[str] = None,
    destination_ip: Optional[str] = None,
    is_suspicious: Optional[bool] = None,
    hours: int = Query(24, le=168),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List network flows"""
    query = db.query(NetworkFlow).filter(
        NetworkFlow.timestamp >= datetime.utcnow() - timedelta(hours=hours)
    )
    
    if source_ip:
        query = query.filter(NetworkFlow.source_ip == source_ip)
    if destination_ip:
        query = query.filter(NetworkFlow.destination_ip == destination_ip)
    if is_suspicious is not None:
        query = query.filter(NetworkFlow.is_suspicious == is_suspicious)
    
    flows = query.order_by(NetworkFlow.timestamp.desc()).offset(offset).limit(limit).all()
    return flows

@router.post("/backups")
async def create_backup_job(backup: BackupJobCreate, db: Session = Depends(get_db)):
    """Create an immutable backup job"""
    engine = CitadelEngine(db)
    job = engine.create_backup_job(
        backup_type=backup.backup_type,
        source=backup.source,
        destination=backup.destination,
        retention_days=backup.retention_days
    )
    return job

@router.get("/backups")
async def list_backup_jobs(
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List backup jobs"""
    query = db.query(BackupJob)
    
    if status:
        query = query.filter(BackupJob.status == status)
    
    jobs = query.order_by(BackupJob.created_at.desc()).offset(offset).limit(limit).all()
    return jobs

@router.get("/siem-alerts")
async def list_siem_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    hours: int = Query(24, le=720),
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List SIEM alerts"""
    query = db.query(SIEMAlert).filter(
        SIEMAlert.detected_at >= datetime.utcnow() - timedelta(hours=hours)
    )
    
    if severity:
        query = query.filter(SIEMAlert.severity == severity)
    if status:
        query = query.filter(SIEMAlert.status == status)
    
    alerts = query.order_by(SIEMAlert.detected_at.desc()).offset(offset).limit(limit).all()
    return alerts

@router.post("/encryption-keys/generate")
async def generate_encryption_key(
    key_type: str,
    algorithm: str,
    purpose: str,
    expires_days: int = 90,
    db: Session = Depends(get_db)
):
    """Generate a new encryption key"""
    engine = CitadelEngine(db)
    key = engine.generate_encryption_key(
        key_type=key_type,
        algorithm=algorithm,
        purpose=purpose,
        expires_days=expires_days
    )
    return key

@router.post("/encryption-keys/rotate")
async def rotate_encryption_keys(db: Session = Depends(get_db)):
    """Rotate expired encryption keys"""
    engine = CitadelEngine(db)
    rotated_keys = engine.rotate_encryption_keys()
    return {
        "rotated_count": len(rotated_keys),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/encryption-keys")
async def list_encryption_keys(
    status: Optional[str] = None,
    key_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List encryption keys"""
    query = db.query(EncryptionKey)
    
    if status:
        query = query.filter(EncryptionKey.status == status)
    if key_type:
        query = query.filter(EncryptionKey.key_type == key_type)
    
    keys = query.order_by(EncryptionKey.created_at.desc()).all()
    return keys

@router.get("/stats/summary")
async def get_monitoring_stats(db: Session = Depends(get_db)):
    """Get monitoring statistics"""
    total_assets = db.query(InfrastructureAsset).count()
    active_assets = db.query(InfrastructureAsset).filter(InfrastructureAsset.status == "active").count()
    
    # Network flows
    suspicious_flows = db.query(NetworkFlow).filter(
        NetworkFlow.is_suspicious == True,
        NetworkFlow.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    # Backups
    pending_backups = db.query(BackupJob).filter(BackupJob.status == "pending").count()
    
    # SIEM alerts
    new_alerts = db.query(SIEMAlert).filter(SIEMAlert.status == "new").count()
    
    return {
        "assets": {
            "total": total_assets,
            "active": active_assets
        },
        "network": {
            "suspicious_flows_24h": suspicious_flows
        },
        "backups": {
            "pending": pending_backups
        },
        "siem": {
            "new_alerts": new_alerts
        }
    }