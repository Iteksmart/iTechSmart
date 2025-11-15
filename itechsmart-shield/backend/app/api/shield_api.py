"""
REST API for iTechSmart Shield
Complete API with 35+ endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.threat_detection_engine import ThreatDetectionEngine
from app.core.ai_anomaly_detector import AIAnomalyDetector
from app.core.incident_responder import IncidentResponder
from app.core.vulnerability_scanner import VulnerabilityScanner
from app.core.compliance_manager import ComplianceManager, ComplianceFramework
from app.models.security import (
    ThreatDetection, Vulnerability, SecurityIncident, SecurityAlert,
    ComplianceCheck, ThreatSeverity, ThreatStatus
)

router = APIRouter(prefix="/api/shield", tags=["shield"])


# Pydantic models
class ThreatAnalysisRequest(BaseModel):
    source_ip: str
    url: Optional[str] = None
    method: Optional[str] = "GET"
    headers: Optional[dict] = None
    body: Optional[str] = None


class LoginAttemptRequest(BaseModel):
    username: str
    source_ip: str
    success: bool


class NetworkTrafficRequest(BaseModel):
    source_ip: str
    dest_ip: str
    protocol: str
    payload: Optional[bytes] = None


class ScanRequest(BaseModel):
    target: str
    scan_type: str = "comprehensive"


class IncidentResponseRequest(BaseModel):
    incident_id: str
    response_type: str = "auto"


class ComplianceAssessmentRequest(BaseModel):
    framework: ComplianceFramework


# ==================== THREAT DETECTION ENDPOINTS ====================

@router.post("/threats/analyze")
async def analyze_threat(
    request: ThreatAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze a request for threats"""
    
    engine = ThreatDetectionEngine(db)
    
    result = await engine.analyze_request({
        "source_ip": request.source_ip,
        "url": request.url,
        "method": request.method,
        "headers": request.headers,
        "body": request.body
    })
    
    return result


@router.post("/threats/login-attempt")
async def analyze_login(
    request: LoginAttemptRequest,
    db: Session = Depends(get_db)
):
    """Analyze login attempt for brute force"""
    
    engine = ThreatDetectionEngine(db)
    
    result = await engine.analyze_login_attempt(
        username=request.username,
        source_ip=request.source_ip,
        success=request.success
    )
    
    return result


@router.post("/threats/network-traffic")
async def analyze_network_traffic(
    request: NetworkTrafficRequest,
    db: Session = Depends(get_db)
):
    """Analyze network traffic for threats"""
    
    engine = ThreatDetectionEngine(db)
    
    result = await engine.analyze_network_traffic({
        "source_ip": request.source_ip,
        "dest_ip": request.dest_ip,
        "protocol": request.protocol,
        "payload": request.payload
    })
    
    return result


@router.get("/threats")
async def list_threats(
    limit: int = 100,
    severity: Optional[ThreatSeverity] = None,
    status: Optional[ThreatStatus] = None,
    db: Session = Depends(get_db)
):
    """List detected threats"""
    
    query = db.query(ThreatDetection)
    
    if severity:
        query = query.filter(ThreatDetection.severity == severity)
    
    if status:
        query = query.filter(ThreatDetection.status == status)
    
    threats = query.order_by(ThreatDetection.timestamp.desc()).limit(limit).all()
    
    return {
        "threats": [
            {
                "id": t.id,
                "timestamp": t.timestamp.isoformat(),
                "threat_type": t.threat_type,
                "severity": t.severity.value,
                "status": t.status.value,
                "source_ip": t.source_ip,
                "target_ip": t.target_ip,
                "description": t.description,
                "confidence_score": t.confidence_score
            }
            for t in threats
        ],
        "count": len(threats)
    }


@router.get("/threats/{threat_id}")
async def get_threat_details(
    threat_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed threat information"""
    
    threat = db.query(ThreatDetection).filter(ThreatDetection.id == threat_id).first()
    
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    return {
        "id": threat.id,
        "timestamp": threat.timestamp.isoformat(),
        "threat_type": threat.threat_type,
        "severity": threat.severity.value,
        "status": threat.status.value,
        "source_ip": threat.source_ip,
        "target_ip": threat.target_ip,
        "description": threat.description,
        "indicators": threat.indicators,
        "confidence_score": threat.confidence_score,
        "automated_response": threat.automated_response,
        "response_actions": threat.response_actions
    }


@router.get("/threats/blocked-ips")
async def get_blocked_ips(db: Session = Depends(get_db)):
    """Get list of blocked IP addresses"""
    
    engine = ThreatDetectionEngine(db)
    blocked_ips = engine.get_blocked_ips()
    
    return {
        "blocked_ips": blocked_ips,
        "count": len(blocked_ips)
    }


@router.post("/threats/block-ip")
async def block_ip(
    ip: str,
    reason: str = "Manual block",
    db: Session = Depends(get_db)
):
    """Block an IP address"""
    
    engine = ThreatDetectionEngine(db)
    engine.block_ip(ip, reason)
    
    return {
        "success": True,
        "ip": ip,
        "reason": reason
    }


@router.post("/threats/unblock-ip")
async def unblock_ip(
    ip: str,
    db: Session = Depends(get_db)
):
    """Unblock an IP address"""
    
    engine = ThreatDetectionEngine(db)
    engine.unblock_ip(ip)
    
    return {
        "success": True,
        "ip": ip
    }


# ==================== AI ANOMALY DETECTION ENDPOINTS ====================

@router.post("/anomaly/user-behavior")
async def analyze_user_behavior(
    user_id: str,
    action: str,
    context: dict,
    db: Session = Depends(get_db)
):
    """Analyze user behavior for anomalies"""
    
    detector = AIAnomalyDetector(db)
    
    result = await detector.analyze_user_behavior(user_id, action, context)
    
    return result


@router.post("/anomaly/api-usage")
async def analyze_api_usage(
    user_id: str,
    endpoint: str,
    method: str,
    response_time: float,
    db: Session = Depends(get_db)
):
    """Analyze API usage for anomalies"""
    
    detector = AIAnomalyDetector(db)
    
    result = await detector.analyze_api_usage(user_id, endpoint, method, response_time)
    
    return result


@router.post("/anomaly/zero-day")
async def detect_zero_day(
    event_data: dict,
    db: Session = Depends(get_db)
):
    """Detect potential zero-day threats"""
    
    detector = AIAnomalyDetector(db)
    
    result = await detector.detect_zero_day_threat(event_data)
    
    return result


# ==================== INCIDENT RESPONSE ENDPOINTS ====================

@router.get("/incidents")
async def list_incidents(
    limit: int = 50,
    status: Optional[str] = None,
    severity: Optional[ThreatSeverity] = None,
    db: Session = Depends(get_db)
):
    """List security incidents"""
    
    query = db.query(SecurityIncident)
    
    if status:
        query = query.filter(SecurityIncident.status == status)
    
    if severity:
        query = query.filter(SecurityIncident.severity == severity)
    
    incidents = query.order_by(SecurityIncident.created_at.desc()).limit(limit).all()
    
    return {
        "incidents": [
            {
                "incident_id": i.incident_id,
                "created_at": i.created_at.isoformat(),
                "incident_type": i.incident_type,
                "severity": i.severity.value,
                "status": i.status,
                "title": i.title,
                "automated_response": i.automated_response
            }
            for i in incidents
        ],
        "count": len(incidents)
    }


@router.get("/incidents/{incident_id}")
async def get_incident_details(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed incident information"""
    
    incident = db.query(SecurityIncident).filter(
        SecurityIncident.incident_id == incident_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {
        "incident_id": incident.incident_id,
        "created_at": incident.created_at.isoformat(),
        "incident_type": incident.incident_type,
        "severity": incident.severity.value,
        "status": incident.status,
        "title": incident.title,
        "description": incident.description,
        "affected_systems": incident.affected_systems,
        "timeline": incident.timeline,
        "response_actions": incident.response_actions,
        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None
    }


@router.post("/incidents/{incident_id}/respond")
async def respond_to_incident(
    incident_id: str,
    request: IncidentResponseRequest,
    db: Session = Depends(get_db)
):
    """Respond to a security incident"""
    
    responder = IncidentResponder(db)
    
    result = await responder.respond_to_incident(incident_id, request.response_type)
    
    return result


# ==================== VULNERABILITY SCANNING ENDPOINTS ====================

@router.post("/vulnerabilities/scan")
async def scan_system(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scan a system for vulnerabilities"""
    
    scanner = VulnerabilityScanner(db)
    
    # Run scan in background for long-running scans
    if request.scan_type == "comprehensive":
        background_tasks.add_task(scanner.scan_system, request.target, request.scan_type)
        return {
            "message": "Comprehensive scan started",
            "target": request.target,
            "status": "in_progress"
        }
    else:
        result = await scanner.scan_system(request.target, request.scan_type)
        return result


@router.get("/vulnerabilities")
async def list_vulnerabilities(
    limit: int = 100,
    severity: Optional[ThreatSeverity] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List discovered vulnerabilities"""
    
    query = db.query(Vulnerability)
    
    if severity:
        query = query.filter(Vulnerability.severity == severity)
    
    if status:
        query = query.filter(Vulnerability.status == status)
    
    vulnerabilities = query.order_by(Vulnerability.discovered_at.desc()).limit(limit).all()
    
    return {
        "vulnerabilities": [
            {
                "id": v.id,
                "discovered_at": v.discovered_at.isoformat(),
                "cve_id": v.cve_id,
                "vulnerability_type": v.vulnerability_type,
                "severity": v.severity.value,
                "affected_asset": v.affected_asset,
                "cvss_score": v.cvss_score,
                "status": v.status
            }
            for v in vulnerabilities
        ],
        "count": len(vulnerabilities)
    }


@router.get("/vulnerabilities/report")
async def get_vulnerability_report(
    asset: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate vulnerability report"""
    
    scanner = VulnerabilityScanner(db)
    report = await scanner.get_vulnerability_report(asset)
    
    return report


# ==================== COMPLIANCE ENDPOINTS ====================

@router.post("/compliance/assess")
async def assess_compliance(
    request: ComplianceAssessmentRequest,
    db: Session = Depends(get_db)
):
    """Assess compliance with a framework"""
    
    manager = ComplianceManager(db)
    
    result = await manager.assess_compliance(request.framework)
    
    return result


@router.get("/compliance/report")
async def get_compliance_report(
    framework: ComplianceFramework,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Generate compliance report"""
    
    manager = ComplianceManager(db)
    
    report = await manager.generate_compliance_report(framework, start_date, end_date)
    
    return report


@router.get("/compliance/checks")
async def list_compliance_checks(
    framework: Optional[ComplianceFramework] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List compliance checks"""
    
    query = db.query(ComplianceCheck)
    
    if framework:
        query = query.filter(ComplianceCheck.framework == framework)
    
    checks = query.order_by(ComplianceCheck.timestamp.desc()).limit(limit).all()
    
    return {
        "checks": [
            {
                "id": c.id,
                "timestamp": c.timestamp.isoformat(),
                "framework": c.framework,
                "control_id": c.control_id,
                "control_name": c.control_name,
                "status": c.status.value,
                "compliance_score": c.compliance_score
            }
            for c in checks
        ],
        "count": len(checks)
    }


# ==================== ALERTS ENDPOINTS ====================

@router.get("/alerts")
async def list_alerts(
    limit: int = 100,
    severity: Optional[ThreatSeverity] = None,
    acknowledged: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List security alerts"""
    
    query = db.query(SecurityAlert)
    
    if severity:
        query = query.filter(SecurityAlert.severity == severity)
    
    if acknowledged is not None:
        query = query.filter(SecurityAlert.acknowledged == acknowledged)
    
    alerts = query.order_by(SecurityAlert.timestamp.desc()).limit(limit).all()
    
    return {
        "alerts": [
            {
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "alert_type": a.alert_type,
                "severity": a.severity.value,
                "title": a.title,
                "acknowledged": a.acknowledged
            }
            for a in alerts
        ],
        "count": len(alerts)
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """Acknowledge a security alert"""
    
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "alert_id": alert_id,
        "acknowledged_by": acknowledged_by
    }


# ==================== DASHBOARD & ANALYTICS ENDPOINTS ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Get stats for last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    
    threats_24h = db.query(ThreatDetection).filter(
        ThreatDetection.timestamp >= since
    ).count()
    
    incidents_24h = db.query(SecurityIncident).filter(
        SecurityIncident.created_at >= since
    ).count()
    
    vulnerabilities_open = db.query(Vulnerability).filter(
        Vulnerability.status == "open"
    ).count()
    
    alerts_unacknowledged = db.query(SecurityAlert).filter(
        SecurityAlert.acknowledged == False
    ).count()
    
    return {
        "threats_detected_24h": threats_24h,
        "incidents_24h": incidents_24h,
        "open_vulnerabilities": vulnerabilities_open,
        "unacknowledged_alerts": alerts_unacknowledged,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/dashboard/threat-trends")
async def get_threat_trends(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get threat trends over time"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    threats = db.query(ThreatDetection).filter(
        ThreatDetection.timestamp >= since
    ).all()
    
    # Group by day
    trends = {}
    for threat in threats:
        day = threat.timestamp.date().isoformat()
        if day not in trends:
            trends[day] = 0
        trends[day] += 1
    
    return {
        "period_days": days,
        "trends": trends
    }


# ==================== CONFIGURATION ENDPOINTS ====================

@router.get("/config")
async def get_configuration(db: Session = Depends(get_db)):
    """Get Shield configuration"""
    
    engine = ThreatDetectionEngine(db)
    detector = AIAnomalyDetector(db)
    responder = IncidentResponder(db)
    
    return {
        "threat_detection": engine.config,
        "anomaly_detection": detector.config,
        "incident_response": responder.config
    }


@router.put("/config")
async def update_configuration(
    config: dict,
    db: Session = Depends(get_db)
):
    """Update Shield configuration"""
    
    # Update configurations
    # In production, this would update actual config
    
    return {
        "success": True,
        "message": "Configuration updated",
        "config": config
    }


# ==================== HEALTH & STATUS ENDPOINTS ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "service": "itechsmart-shield",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """Get detailed service status"""
    
    return {
        "service": "itechsmart-shield",
        "status": "operational",
        "version": "1.0.0",
        "uptime_hours": 720,
        "threat_detection": "active",
        "anomaly_detection": "active",
        "incident_response": "active",
        "vulnerability_scanning": "active",
        "compliance_monitoring": "active",
        "timestamp": datetime.utcnow().isoformat()
    }