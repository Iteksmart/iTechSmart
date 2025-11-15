"""
iTechSmart Citadel - Database Models
Sovereign Digital Infrastructure Platform

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class SecurityEvent(Base):
    """Security events and incidents"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)  # intrusion, malware, anomaly, etc.
    severity = Column(String(50), nullable=False)  # critical, high, medium, low
    source = Column(String(255), nullable=False)
    destination = Column(String(255))
    description = Column(Text, nullable=False)
    status = Column(String(50), default="open")  # open, investigating, resolved, false_positive
    threat_level = Column(Integer, default=0)  # 0-100
    metadata = Column(JSON, default={})
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ThreatIntelligence(Base):
    """Threat intelligence data"""
    __tablename__ = "threat_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    threat_type = Column(String(100), nullable=False)  # malware, botnet, c2, phishing
    indicator = Column(String(500), nullable=False)  # IP, domain, hash, etc.
    indicator_type = Column(String(50), nullable=False)  # ip, domain, hash, url
    confidence = Column(Float, default=0.0)  # 0.0-1.0
    severity = Column(String(50), nullable=False)
    description = Column(Text)
    source = Column(String(255))  # threat feed source
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class CompliancePolicy(Base):
    """Compliance policies and frameworks"""
    __tablename__ = "compliance_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    framework = Column(String(100), nullable=False)  # HIPAA, PCI-DSS, SOC2, ISO27001
    description = Column(Text)
    requirements = Column(JSON, default=[])
    enabled = Column(Boolean, default=True)
    enforcement_level = Column(String(50), default="monitor")  # monitor, enforce, audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComplianceCheck(Base):
    """Compliance check results"""
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("compliance_policies.id"))
    check_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # passed, failed, warning, not_applicable
    score = Column(Float, default=0.0)  # 0.0-100.0
    findings = Column(JSON, default=[])
    remediation = Column(Text)
    checked_at = Column(DateTime, default=datetime.utcnow)
    
    policy = relationship("CompliancePolicy")

class InfrastructureAsset(Base):
    """Infrastructure assets under protection"""
    __tablename__ = "infrastructure_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(100), nullable=False)  # server, container, network, application
    name = Column(String(255), nullable=False)
    hostname = Column(String(255))
    ip_address = Column(String(50))
    location = Column(String(255))
    environment = Column(String(50))  # production, staging, development
    criticality = Column(String(50), default="medium")  # critical, high, medium, low
    status = Column(String(50), default="active")
    os_type = Column(String(100))
    os_version = Column(String(100))
    metadata = Column(JSON, default={})
    last_scan = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vulnerability(Base):
    """Vulnerability tracking"""
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"))
    cve_id = Column(String(50))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(50), nullable=False)  # critical, high, medium, low
    cvss_score = Column(Float)
    cvss_vector = Column(String(255))
    status = Column(String(50), default="open")  # open, patching, patched, accepted, false_positive
    exploit_available = Column(Boolean, default=False)
    patch_available = Column(Boolean, default=False)
    remediation = Column(Text)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    patched_at = Column(DateTime, nullable=True)
    
    asset = relationship("InfrastructureAsset")

class SecurityControl(Base):
    """Security controls and configurations"""
    __tablename__ = "security_controls"
    
    id = Column(Integer, primary_key=True, index=True)
    control_type = Column(String(100), nullable=False)  # firewall, ids, ips, encryption
    name = Column(String(255), nullable=False)
    description = Column(Text)
    configuration = Column(JSON, default={})
    enabled = Column(Boolean, default=True)
    effectiveness = Column(Float, default=0.0)  # 0.0-100.0
    last_tested = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IncidentResponse(Base):
    """Incident response actions"""
    __tablename__ = "incident_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("security_events.id"))
    action_type = Column(String(100), nullable=False)  # isolate, block, investigate, remediate
    action_taken = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    result = Column(JSON, default={})
    initiated_by = Column(String(255))
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    event = relationship("SecurityEvent")

class AuditLog(Base):
    """Comprehensive audit logging"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    user = Column(String(255))
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    status = Column(String(50), nullable=False)  # success, failure
    details = Column(JSON, default={})
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class EncryptionKey(Base):
    """Post-quantum encryption key management"""
    __tablename__ = "encryption_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_type = Column(String(100), nullable=False)  # quantum_resistant, symmetric, asymmetric
    algorithm = Column(String(100), nullable=False)  # CRYSTALS-Kyber, CRYSTALS-Dilithium, etc.
    key_id = Column(String(255), unique=True, nullable=False)
    purpose = Column(String(255))  # encryption, signing, key_exchange
    status = Column(String(50), default="active")  # active, rotated, revoked
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    rotated_at = Column(DateTime, nullable=True)

class NetworkFlow(Base):
    """Network traffic analysis"""
    __tablename__ = "network_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String(50), nullable=False)
    source_port = Column(Integer)
    destination_ip = Column(String(50), nullable=False)
    destination_port = Column(Integer)
    protocol = Column(String(20), nullable=False)
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    flags = Column(String(100))
    is_suspicious = Column(Boolean, default=False)
    threat_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class BackupJob(Base):
    """Immutable backup tracking"""
    __tablename__ = "backup_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    backup_type = Column(String(50), nullable=False)  # full, incremental, differential
    source = Column(String(500), nullable=False)
    destination = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    size_bytes = Column(Integer, default=0)
    encrypted = Column(Boolean, default=True)
    immutable = Column(Boolean, default=True)
    retention_days = Column(Integer, default=90)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class SIEMAlert(Base):
    """SIEM/XDR alerts"""
    __tablename__ = "siem_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    source_system = Column(String(255))
    affected_assets = Column(JSON, default=[])
    indicators = Column(JSON, default=[])
    status = Column(String(50), default="new")  # new, investigating, resolved, false_positive
    confidence = Column(Float, default=0.0)
    metadata = Column(JSON, default={})
    detected_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

class ZeroTrustPolicy(Base):
    """Zero Trust access policies"""
    __tablename__ = "zero_trust_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    policy_type = Column(String(100), nullable=False)  # access, network, device
    conditions = Column(JSON, default={})
    actions = Column(JSON, default={})
    priority = Column(Integer, default=100)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HardwareSecurityModule(Base):
    """HSM and secure enclave management"""
    __tablename__ = "hardware_security_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    module_type = Column(String(100), nullable=False)  # hsm, tpm, secure_enclave
    name = Column(String(255), nullable=False)
    serial_number = Column(String(255), unique=True)
    status = Column(String(50), default="active")
    capabilities = Column(JSON, default=[])
    location = Column(String(255))
    last_health_check = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)