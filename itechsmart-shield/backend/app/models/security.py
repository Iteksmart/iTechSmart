"""
Database models for iTechSmart Shield
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float, Enum
from datetime import datetime
import enum

from app.core.database import Base


class ThreatSeverity(str, enum.Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatStatus(str, enum.Enum):
    """Threat status"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class ComplianceStatus(str, enum.Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"


class ThreatDetection(Base):
    """Detected security threats"""
    __tablename__ = "threat_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    threat_type = Column(String(100), index=True)  # malware, intrusion, ddos, etc.
    severity = Column(Enum(ThreatSeverity), index=True)
    status = Column(Enum(ThreatStatus), default=ThreatStatus.DETECTED)
    source_ip = Column(String(50), index=True)
    target_ip = Column(String(50), index=True)
    source_port = Column(Integer, nullable=True)
    target_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)
    description = Column(Text)
    indicators = Column(JSON)  # IOCs (Indicators of Compromise)
    affected_assets = Column(JSON)  # List of affected systems
    attack_vector = Column(String(100), nullable=True)
    confidence_score = Column(Float)  # AI confidence 0-1
    false_positive_probability = Column(Float, nullable=True)
    mitre_attack_id = Column(String(50), nullable=True)  # MITRE ATT&CK framework
    automated_response = Column(Boolean, default=False)
    response_actions = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)


class Vulnerability(Base):
    """Detected vulnerabilities"""
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    cve_id = Column(String(50), index=True, nullable=True)  # CVE identifier
    vulnerability_type = Column(String(100), index=True)
    severity = Column(Enum(ThreatSeverity), index=True)
    cvss_score = Column(Float, nullable=True)  # CVSS score 0-10
    affected_asset = Column(String(200), index=True)
    asset_type = Column(String(50))  # server, application, network_device, etc.
    description = Column(Text)
    remediation = Column(Text)
    exploit_available = Column(Boolean, default=False)
    exploited = Column(Boolean, default=False)
    patched = Column(Boolean, default=False)
    patch_available = Column(Boolean, default=False)
    patch_version = Column(String(50), nullable=True)
    risk_score = Column(Float)  # Calculated risk score
    status = Column(String(50), default="open")  # open, in_progress, patched, accepted
    assigned_to = Column(String(100), nullable=True)
    due_date = Column(DateTime, nullable=True)
    patched_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)


class SecurityIncident(Base):
    """Security incidents"""
    __tablename__ = "security_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    incident_type = Column(String(100), index=True)
    severity = Column(Enum(ThreatSeverity), index=True)
    status = Column(String(50), default="open")  # open, investigating, contained, resolved
    title = Column(String(200))
    description = Column(Text)
    affected_systems = Column(JSON)
    impact_assessment = Column(Text)
    root_cause = Column(Text, nullable=True)
    timeline = Column(JSON)  # Timeline of events
    response_actions = Column(JSON)
    automated_response = Column(Boolean, default=False)
    assigned_to = Column(String(100), nullable=True)
    escalated = Column(Boolean, default=False)
    escalated_to = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_summary = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)
    cost_estimate = Column(Float, nullable=True)


class SecurityAlert(Base):
    """Security alerts"""
    __tablename__ = "security_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_type = Column(String(100), index=True)
    severity = Column(Enum(ThreatSeverity), index=True)
    source = Column(String(100))  # IDS, IPS, firewall, etc.
    title = Column(String(200))
    description = Column(Text)
    details = Column(JSON)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    false_positive = Column(Boolean, default=False)
    correlated_alerts = Column(JSON, nullable=True)  # Related alert IDs
    incident_id = Column(Integer, nullable=True)  # Linked incident


class ComplianceCheck(Base):
    """Compliance check results"""
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    framework = Column(String(50), index=True)  # SOC2, ISO27001, GDPR, HIPAA
    control_id = Column(String(50), index=True)
    control_name = Column(String(200))
    control_description = Column(Text)
    status = Column(Enum(ComplianceStatus))
    compliance_score = Column(Float)  # 0-100
    findings = Column(JSON)
    evidence = Column(JSON, nullable=True)
    gaps = Column(JSON, nullable=True)
    remediation_plan = Column(Text, nullable=True)
    responsible_party = Column(String(100), nullable=True)
    due_date = Column(DateTime, nullable=True)
    last_assessed = Column(DateTime, default=datetime.utcnow)
    next_assessment = Column(DateTime, nullable=True)


class SecurityPolicy(Base):
    """Security policies"""
    __tablename__ = "security_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    description = Column(Text)
    policy_type = Column(String(50))  # access_control, encryption, password, etc.
    rules = Column(JSON)
    enabled = Column(Boolean, default=True)
    enforcement_level = Column(String(20))  # strict, moderate, advisory
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    violations = Column(Integer, default=0)
    last_violation = Column(DateTime, nullable=True)


class ThreatIntelligence(Base):
    """Threat intelligence data"""
    __tablename__ = "threat_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ioc_type = Column(String(50), index=True)  # ip, domain, hash, url, email
    ioc_value = Column(String(500), index=True)
    threat_type = Column(String(100))
    severity = Column(Enum(ThreatSeverity))
    confidence = Column(Float)  # 0-1
    source = Column(String(100))  # Threat intel feed source
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    tags = Column(JSON)
    context = Column(JSON)
    related_campaigns = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    blocked = Column(Boolean, default=False)


class SecurityAuditLog(Base):
    """Security audit trail"""
    __tablename__ = "security_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(100), index=True)
    user = Column(String(100), index=True)
    source_ip = Column(String(50))
    action = Column(String(100))
    resource = Column(String(200))
    result = Column(String(20))  # success, failure, denied
    details = Column(JSON)
    risk_score = Column(Float, nullable=True)
    anomaly_detected = Column(Boolean, default=False)


class SecurityMetric(Base):
    """Security metrics and KPIs"""
    __tablename__ = "security_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String(50), index=True)
    metric_name = Column(String(100))
    metric_value = Column(Float)
    unit = Column(String(20))
    threshold = Column(Float, nullable=True)
    threshold_exceeded = Column(Boolean, default=False)
    context = Column(JSON, nullable=True)


class PenetrationTest(Base):
    """Penetration testing results"""
    __tablename__ = "penetration_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(50), unique=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    test_type = Column(String(50))  # network, web_app, social_engineering, etc.
    scope = Column(JSON)  # Target systems/applications
    methodology = Column(String(100))  # OWASP, PTES, etc.
    findings = Column(JSON)
    vulnerabilities_found = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    status = Column(String(50), default="in_progress")
    report_path = Column(String(500), nullable=True)
    conducted_by = Column(String(100))
    automated = Column(Boolean, default=False)


class SecurityPosture(Base):
    """Overall security posture assessment"""
    __tablename__ = "security_posture"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    overall_score = Column(Float)  # 0-100
    threat_level = Column(String(20))  # low, moderate, high, critical
    active_threats = Column(Integer, default=0)
    open_vulnerabilities = Column(Integer, default=0)
    critical_vulnerabilities = Column(Integer, default=0)
    compliance_score = Column(Float)  # 0-100
    risk_score = Column(Float)  # 0-100
    security_controls = Column(JSON)
    recommendations = Column(JSON)
    trends = Column(JSON, nullable=True)