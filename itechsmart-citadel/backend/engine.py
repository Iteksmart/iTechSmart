"""
iTechSmart Citadel - Core Engine
Sovereign Digital Infrastructure Security Engine

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import requests
import redis

from models import (
    SecurityEvent,
    ThreatIntelligence,
    CompliancePolicy,
    ComplianceCheck,
    InfrastructureAsset,
    Vulnerability,
    SecurityControl,
    IncidentResponse,
    AuditLog,
    EncryptionKey,
    NetworkFlow,
    BackupJob,
    SIEMAlert,
    ZeroTrustPolicy,
    HardwareSecurityModule,
)
from config import settings, SECURITY_EVENT_TYPES, COMPLIANCE_FRAMEWORKS_CONFIG

logger = logging.getLogger(__name__)


class CitadelEngine:
    """Core engine for sovereign digital infrastructure security"""

    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis.from_url(settings.REDIS_URL)

    # ==================== SECURITY EVENT MANAGEMENT ====================

    def create_security_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
        destination: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> SecurityEvent:
        """Create a new security event"""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            destination=destination,
            description=description,
            status="open",
            threat_level=self._calculate_threat_level(event_type, severity),
            metadata=metadata or {},
            detected_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        logger.info(
            f"Created security event #{event.id}: {event_type} (severity: {severity})"
        )

        # Trigger auto-response if configured
        event_config = SECURITY_EVENT_TYPES.get(event_type, {})
        if event_config.get("auto_response"):
            self._trigger_auto_response(event)

        # Create SIEM alert
        self._create_siem_alert(event)

        return event

    def _calculate_threat_level(self, event_type: str, severity: str) -> int:
        """Calculate threat level (0-100)"""
        severity_scores = {"critical": 90, "high": 70, "medium": 50, "low": 30}

        event_multipliers = {
            "intrusion": 1.0,
            "malware": 1.0,
            "data_exfiltration": 1.0,
            "unauthorized_access": 0.9,
            "anomaly": 0.7,
            "policy_violation": 0.5,
        }

        base_score = severity_scores.get(severity, 50)
        multiplier = event_multipliers.get(event_type, 0.8)

        return min(100, int(base_score * multiplier))

    def _trigger_auto_response(self, event: SecurityEvent):
        """Trigger automated incident response"""
        event_config = SECURITY_EVENT_TYPES.get(event.event_type, {})
        actions = event_config.get("actions", [])

        for action_type in actions:
            self.create_incident_response(
                event_id=event.id,
                action_type=action_type,
                action_taken=f"Automated {action_type} response triggered",
                initiated_by="system",
            )

    # ==================== THREAT INTELLIGENCE ====================

    def add_threat_indicator(
        self,
        threat_type: str,
        indicator: str,
        indicator_type: str,
        confidence: float,
        severity: str,
        description: Optional[str] = None,
        source: Optional[str] = None,
    ) -> ThreatIntelligence:
        """Add threat intelligence indicator"""
        threat = ThreatIntelligence(
            threat_type=threat_type,
            indicator=indicator,
            indicator_type=indicator_type,
            confidence=confidence,
            severity=severity,
            description=description,
            source=source,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(threat)
        self.db.commit()
        self.db.refresh(threat)

        logger.info(f"Added threat indicator: {indicator} (type: {threat_type})")
        return threat

    def check_threat_indicator(
        self, indicator: str, indicator_type: str
    ) -> Optional[ThreatIntelligence]:
        """Check if indicator is in threat intelligence database"""
        threat = (
            self.db.query(ThreatIntelligence)
            .filter(
                ThreatIntelligence.indicator == indicator,
                ThreatIntelligence.indicator_type == indicator_type,
                ThreatIntelligence.is_active == True,
            )
            .first()
        )

        if threat:
            # Update last seen
            threat.last_seen = datetime.utcnow()
            self.db.commit()

        return threat

    def update_threat_feeds(self) -> Dict:
        """Update threat intelligence feeds"""
        # Placeholder for threat feed integration
        # In production, integrate with threat intelligence providers
        logger.info("Updating threat intelligence feeds")
        return {"status": "updated", "timestamp": datetime.utcnow().isoformat()}

    # ==================== COMPLIANCE MANAGEMENT ====================

    def create_compliance_policy(
        self, name: str, framework: str, description: str, requirements: List[str]
    ) -> CompliancePolicy:
        """Create a compliance policy"""
        policy = CompliancePolicy(
            name=name,
            framework=framework,
            description=description,
            requirements=requirements,
            enabled=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)

        logger.info(f"Created compliance policy: {name} ({framework})")
        return policy

    def run_compliance_check(self, policy_id: int) -> List[ComplianceCheck]:
        """Run compliance checks for a policy"""
        policy = (
            self.db.query(CompliancePolicy)
            .filter(CompliancePolicy.id == policy_id)
            .first()
        )

        if not policy:
            raise ValueError(f"Policy {policy_id} not found")

        checks = []
        for requirement in policy.requirements:
            # Perform compliance check (simplified)
            check_result = self._perform_compliance_check(policy.framework, requirement)

            check = ComplianceCheck(
                policy_id=policy_id,
                check_name=requirement,
                status=check_result["status"],
                score=check_result["score"],
                findings=check_result["findings"],
                remediation=check_result.get("remediation"),
                checked_at=datetime.utcnow(),
            )
            checks.append(check)
            self.db.add(check)

        self.db.commit()
        logger.info(
            f"Completed {len(checks)} compliance checks for policy #{policy_id}"
        )
        return checks

    def _perform_compliance_check(self, framework: str, requirement: str) -> Dict:
        """Perform individual compliance check"""
        # Simplified compliance check logic
        # In production, implement actual compliance validation
        return {"status": "passed", "score": 95.0, "findings": [], "remediation": None}

    def get_compliance_score(self, framework: str) -> float:
        """Calculate overall compliance score for a framework"""
        policies = (
            self.db.query(CompliancePolicy)
            .filter(
                CompliancePolicy.framework == framework,
                CompliancePolicy.enabled == True,
            )
            .all()
        )

        if not policies:
            return 0.0

        total_score = 0.0
        total_checks = 0

        for policy in policies:
            checks = (
                self.db.query(ComplianceCheck)
                .filter(ComplianceCheck.policy_id == policy.id)
                .all()
            )

            for check in checks:
                total_score += check.score
                total_checks += 1

        return total_score / total_checks if total_checks > 0 else 0.0

    # ==================== VULNERABILITY MANAGEMENT ====================

    def add_vulnerability(
        self,
        asset_id: int,
        title: str,
        severity: str,
        description: Optional[str] = None,
        cve_id: Optional[str] = None,
        cvss_score: Optional[float] = None,
    ) -> Vulnerability:
        """Add a vulnerability"""
        vuln = Vulnerability(
            asset_id=asset_id,
            cve_id=cve_id,
            title=title,
            description=description,
            severity=severity,
            cvss_score=cvss_score,
            status="open",
            discovered_at=datetime.utcnow(),
        )
        self.db.add(vuln)
        self.db.commit()
        self.db.refresh(vuln)

        logger.info(f"Added vulnerability: {title} (severity: {severity})")

        # Create security event for critical vulnerabilities
        if severity == "critical":
            self.create_security_event(
                event_type="vulnerability",
                severity="critical",
                source=f"asset_{asset_id}",
                description=f"Critical vulnerability discovered: {title}",
            )

        return vuln

    def scan_asset_vulnerabilities(self, asset_id: int) -> List[Vulnerability]:
        """Scan an asset for vulnerabilities"""
        asset = (
            self.db.query(InfrastructureAsset)
            .filter(InfrastructureAsset.id == asset_id)
            .first()
        )

        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Placeholder for vulnerability scanning
        # In production, integrate with vulnerability scanners
        logger.info(f"Scanning asset #{asset_id} for vulnerabilities")

        asset.last_scan = datetime.utcnow()
        self.db.commit()

        return []

    # ==================== INCIDENT RESPONSE ====================

    def create_incident_response(
        self, event_id: int, action_type: str, action_taken: str, initiated_by: str
    ) -> IncidentResponse:
        """Create an incident response action"""
        response = IncidentResponse(
            event_id=event_id,
            action_type=action_type,
            action_taken=action_taken,
            status="pending",
            initiated_by=initiated_by,
            initiated_at=datetime.utcnow(),
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)

        logger.info(f"Created incident response #{response.id}: {action_type}")
        return response

    def execute_incident_response(self, response_id: int) -> Dict:
        """Execute an incident response action"""
        response = (
            self.db.query(IncidentResponse)
            .filter(IncidentResponse.id == response_id)
            .first()
        )

        if not response:
            raise ValueError(f"Response {response_id} not found")

        response.status = "in_progress"
        self.db.commit()

        try:
            # Execute response action
            result = self._execute_response_action(response)

            response.status = "completed"
            response.result = result
            response.completed_at = datetime.utcnow()
            self.db.commit()

            return result
        except Exception as e:
            response.status = "failed"
            response.result = {"error": str(e)}
            response.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def _execute_response_action(self, response: IncidentResponse) -> Dict:
        """Execute specific response action"""
        # Placeholder for actual response execution
        # In production, implement actual security actions
        return {
            "success": True,
            "action": response.action_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ==================== ENCRYPTION &amp; KEY MANAGEMENT ====================

    def generate_encryption_key(
        self, key_type: str, algorithm: str, purpose: str, expires_days: int = 90
    ) -> EncryptionKey:
        """Generate a new encryption key"""
        key_id = self._generate_key_id()

        key = EncryptionKey(
            key_type=key_type,
            algorithm=algorithm,
            key_id=key_id,
            purpose=purpose,
            status="active",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
        )
        self.db.add(key)
        self.db.commit()
        self.db.refresh(key)

        logger.info(f"Generated encryption key: {key_id} ({algorithm})")
        return key

    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:32]

    def rotate_encryption_keys(self) -> List[EncryptionKey]:
        """Rotate expired encryption keys"""
        expired_keys = (
            self.db.query(EncryptionKey)
            .filter(
                EncryptionKey.status == "active",
                EncryptionKey.expires_at <= datetime.utcnow(),
            )
            .all()
        )

        rotated_keys = []
        for old_key in expired_keys:
            # Create new key
            new_key = self.generate_encryption_key(
                key_type=old_key.key_type,
                algorithm=old_key.algorithm,
                purpose=old_key.purpose,
            )

            # Mark old key as rotated
            old_key.status = "rotated"
            old_key.rotated_at = datetime.utcnow()

            rotated_keys.append(new_key)

        self.db.commit()
        logger.info(f"Rotated {len(rotated_keys)} encryption keys")
        return rotated_keys

    # ==================== NETWORK MONITORING ====================

    def analyze_network_flow(
        self,
        source_ip: str,
        destination_ip: str,
        protocol: str,
        bytes_sent: int = 0,
        bytes_received: int = 0,
    ) -> NetworkFlow:
        """Analyze and record network flow"""
        # Check for suspicious patterns
        is_suspicious, threat_score = self._analyze_flow_patterns(
            source_ip, destination_ip, protocol, bytes_sent, bytes_received
        )

        flow = NetworkFlow(
            source_ip=source_ip,
            destination_ip=destination_ip,
            protocol=protocol,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            is_suspicious=is_suspicious,
            threat_score=threat_score,
            timestamp=datetime.utcnow(),
        )
        self.db.add(flow)
        self.db.commit()
        self.db.refresh(flow)

        # Create security event if suspicious
        if is_suspicious and threat_score > 70:
            self.create_security_event(
                event_type="anomaly",
                severity="high",
                source=source_ip,
                destination=destination_ip,
                description=f"Suspicious network flow detected (threat score: {threat_score})",
            )

        return flow

    def _analyze_flow_patterns(
        self,
        source_ip: str,
        destination_ip: str,
        protocol: str,
        bytes_sent: int,
        bytes_received: int,
    ) -> tuple:
        """Analyze network flow for suspicious patterns"""
        threat_score = 0.0

        # Check against threat intelligence
        threat = self.check_threat_indicator(source_ip, "ip")
        if threat:
            threat_score += 50.0

        threat = self.check_threat_indicator(destination_ip, "ip")
        if threat:
            threat_score += 50.0

        # Check for unusual data transfer
        if bytes_sent > 1000000000 or bytes_received > 1000000000:  # > 1GB
            threat_score += 20.0

        is_suspicious = threat_score > 50.0
        return is_suspicious, min(100.0, threat_score)

    # ==================== SIEM ALERTS ====================

    def _create_siem_alert(self, event: SecurityEvent):
        """Create SIEM alert from security event"""
        alert = SIEMAlert(
            alert_type=event.event_type,
            severity=event.severity,
            title=event.description[:500],
            description=event.description,
            source_system="citadel",
            status="new",
            confidence=0.8,
            detected_at=event.detected_at,
        )
        self.db.add(alert)
        self.db.commit()

    # ==================== BACKUP MANAGEMENT ====================

    def create_backup_job(
        self, backup_type: str, source: str, destination: str, retention_days: int = 90
    ) -> BackupJob:
        """Create an immutable backup job"""
        job = BackupJob(
            backup_type=backup_type,
            source=source,
            destination=destination,
            status="pending",
            encrypted=settings.BACKUP_ENCRYPTION,
            immutable=settings.IMMUTABLE_BACKUP_ENABLED,
            retention_days=retention_days,
            created_at=datetime.utcnow(),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        logger.info(f"Created backup job #{job.id}: {backup_type}")
        return job

    # ==================== AUDIT LOGGING ====================

    def log_audit_event(
        self,
        event_type: str,
        action: str,
        status: str,
        user: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        """Log audit event"""
        log = AuditLog(
            event_type=event_type,
            user=user,
            action=action,
            resource=resource,
            status=status,
            details=details or {},
            timestamp=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
