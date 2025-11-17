"""
Security Monitoring System
Real-time security monitoring and alerting
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(Enum):
    """Security event types"""

    FAILED_LOGIN = "failed_login"
    BRUTE_FORCE = "brute_force"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH = "data_breach"
    MALWARE_DETECTED = "malware_detected"
    DOS_ATTACK = "dos_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


class SecurityMonitor:
    """
    Real-time security monitoring and threat detection
    """

    def __init__(self):
        self.alerts = []
        self.failed_login_attempts = defaultdict(list)
        self.suspicious_ips = set()
        self.blocked_ips = set()
        self.rate_violations = defaultdict(int)

    # ========================================================================
    # Authentication Monitoring
    # ========================================================================

    def monitor_login_attempt(
        self,
        username: str,
        ip_address: str,
        success: bool,
        timestamp: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Monitor login attempts for brute force attacks
        """
        timestamp = timestamp or datetime.now()

        if not success:
            # Track failed login
            self.failed_login_attempts[username].append(
                {"ip_address": ip_address, "timestamp": timestamp}
            )

            # Check for brute force attack
            recent_failures = self._get_recent_failures(username, minutes=15)

            if len(recent_failures) >= 5:
                # Brute force detected
                alert = self._create_alert(
                    event_type=SecurityEvent.BRUTE_FORCE,
                    threat_level=ThreatLevel.HIGH,
                    description=f"Brute force attack detected for user {username}",
                    details={
                        "username": username,
                        "ip_address": ip_address,
                        "failed_attempts": len(recent_failures),
                        "time_window": "15 minutes",
                    },
                    recommended_actions=[
                        f"Block IP address: {ip_address}",
                        f"Lock account: {username}",
                        "Notify security team",
                        "Review access logs",
                    ],
                )

                # Auto-block IP
                self.block_ip(ip_address, reason="Brute force attack")

                return alert

        return None

    def _get_recent_failures(self, username: str, minutes: int = 15) -> List[Dict]:
        """
        Get recent failed login attempts
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        failures = self.failed_login_attempts.get(username, [])

        return [f for f in failures if f["timestamp"] > cutoff]

    # ========================================================================
    # Access Monitoring
    # ========================================================================

    def monitor_access_attempt(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        resource_id: str,
        action: str,
        allowed: bool,
        ip_address: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Monitor resource access attempts
        """
        if not allowed:
            # Unauthorized access attempt
            alert = self._create_alert(
                event_type=SecurityEvent.UNAUTHORIZED_ACCESS,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Unauthorized access attempt by {username}",
                details={
                    "user_id": user_id,
                    "username": username,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "action": action,
                    "ip_address": ip_address,
                },
                recommended_actions=[
                    "Review user permissions",
                    "Verify user identity",
                    "Check for account compromise",
                ],
            )

            # Track suspicious activity
            self._track_suspicious_activity(user_id, ip_address)

            return alert

        return None

    def _track_suspicious_activity(self, user_id: str, ip_address: Optional[str]):
        """
        Track suspicious activity patterns
        """
        if ip_address:
            self.suspicious_ips.add(ip_address)

    # ========================================================================
    # Rate Limit Monitoring
    # ========================================================================

    def monitor_rate_limit_violation(
        self, client_id: str, endpoint: str, violation_count: int
    ) -> Optional[Dict[str, Any]]:
        """
        Monitor rate limit violations
        """
        self.rate_violations[client_id] += 1

        if self.rate_violations[client_id] >= 10:
            # Potential DoS attack
            alert = self._create_alert(
                event_type=SecurityEvent.DOS_ATTACK,
                threat_level=ThreatLevel.HIGH,
                description=f"Potential DoS attack from {client_id}",
                details={
                    "client_id": client_id,
                    "endpoint": endpoint,
                    "violation_count": violation_count,
                    "total_violations": self.rate_violations[client_id],
                },
                recommended_actions=[
                    f"Block client: {client_id}",
                    "Increase rate limits temporarily",
                    "Analyze traffic patterns",
                    "Contact client if legitimate",
                ],
            )

            return alert

        return None

    # ========================================================================
    # Data Access Monitoring
    # ========================================================================

    def monitor_data_access(
        self,
        user_id: str,
        username: str,
        patient_count: int,
        time_window_minutes: int = 5,
    ) -> Optional[Dict[str, Any]]:
        """
        Monitor for unusual data access patterns
        """
        # Check for mass data access
        if patient_count > 50:
            alert = self._create_alert(
                event_type=SecurityEvent.SUSPICIOUS_ACTIVITY,
                threat_level=ThreatLevel.HIGH,
                description=f"Mass data access detected for user {username}",
                details={
                    "user_id": user_id,
                    "username": username,
                    "patient_count": patient_count,
                    "time_window": f"{time_window_minutes} minutes",
                },
                recommended_actions=[
                    "Verify user activity is legitimate",
                    "Check for data exfiltration",
                    "Review user permissions",
                    "Contact user for verification",
                ],
            )

            return alert

        return None

    def monitor_data_export(
        self, user_id: str, username: str, record_count: int, export_format: str
    ) -> Optional[Dict[str, Any]]:
        """
        Monitor data exports
        """
        # Check for large exports
        if record_count > 1000:
            alert = self._create_alert(
                event_type=SecurityEvent.SUSPICIOUS_ACTIVITY,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Large data export by {username}",
                details={
                    "user_id": user_id,
                    "username": username,
                    "record_count": record_count,
                    "export_format": export_format,
                },
                recommended_actions=[
                    "Verify export is authorized",
                    "Review export contents",
                    "Check data classification",
                    "Ensure proper encryption",
                ],
            )

            return alert

        return None

    # ========================================================================
    # Anomaly Detection
    # ========================================================================

    def detect_anomalous_behavior(
        self, user_id: str, username: str, behavior_metrics: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect anomalous user behavior
        """
        anomalies = []

        # Check for unusual access times
        if behavior_metrics.get("access_time"):
            hour = datetime.now().hour
            if hour < 6 or hour > 22:
                anomalies.append("Access outside normal hours")

        # Check for unusual access patterns
        if behavior_metrics.get("access_count", 0) > 100:
            anomalies.append("Unusually high access count")

        # Check for unusual locations
        if behavior_metrics.get("new_location"):
            anomalies.append("Access from new location")

        if anomalies:
            alert = self._create_alert(
                event_type=SecurityEvent.ANOMALOUS_BEHAVIOR,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Anomalous behavior detected for user {username}",
                details={
                    "user_id": user_id,
                    "username": username,
                    "anomalies": anomalies,
                    "metrics": behavior_metrics,
                },
                recommended_actions=[
                    "Verify user identity",
                    "Check for account compromise",
                    "Review recent activity",
                    "Contact user for verification",
                ],
            )

            return alert

        return None

    # ========================================================================
    # IP Management
    # ========================================================================

    def block_ip(self, ip_address: str, reason: str):
        """
        Block IP address
        """
        self.blocked_ips.add(ip_address)
        logger.warning(f"Blocked IP {ip_address}: {reason}")

    def unblock_ip(self, ip_address: str):
        """
        Unblock IP address
        """
        self.blocked_ips.discard(ip_address)
        logger.info(f"Unblocked IP {ip_address}")

    def is_ip_blocked(self, ip_address: str) -> bool:
        """
        Check if IP is blocked
        """
        return ip_address in self.blocked_ips

    # ========================================================================
    # Alert Management
    # ========================================================================

    def _create_alert(
        self,
        event_type: SecurityEvent,
        threat_level: ThreatLevel,
        description: str,
        details: Dict[str, Any],
        recommended_actions: List[str],
    ) -> Dict[str, Any]:
        """
        Create security alert
        """
        alert = {
            "id": len(self.alerts) + 1,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "threat_level": threat_level.value,
            "description": description,
            "details": details,
            "recommended_actions": recommended_actions,
            "status": "open",
            "acknowledged": False,
        }

        self.alerts.append(alert)

        # Log alert
        logger.warning(f"Security Alert [{threat_level.value}]: {description}")

        # Send notifications for high/critical alerts
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._send_alert_notification(alert)

        return alert

    def _send_alert_notification(self, alert: Dict[str, Any]):
        """
        Send alert notification (email, SMS, etc.)
        """
        # This would integrate with notification service
        logger.critical(f"CRITICAL ALERT: {alert['description']}")

    def get_alerts(
        self,
        threat_level: Optional[ThreatLevel] = None,
        event_type: Optional[SecurityEvent] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get security alerts with filters
        """
        filtered_alerts = self.alerts

        if threat_level:
            filtered_alerts = [
                a for a in filtered_alerts if a["threat_level"] == threat_level.value
            ]

        if event_type:
            filtered_alerts = [
                a for a in filtered_alerts if a["event_type"] == event_type.value
            ]

        if status:
            filtered_alerts = [a for a in filtered_alerts if a["status"] == status]

        return filtered_alerts[-limit:]

    def acknowledge_alert(self, alert_id: int, acknowledged_by: str):
        """
        Acknowledge security alert
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_by"] = acknowledged_by
                alert["acknowledged_at"] = datetime.now().isoformat()
                logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                break

    def resolve_alert(self, alert_id: int, resolved_by: str, resolution: str):
        """
        Resolve security alert
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_by"] = resolved_by
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolution"] = resolution
                logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                break

    # ========================================================================
    # Security Metrics
    # ========================================================================

    def get_security_metrics(self) -> Dict[str, Any]:
        """
        Get security metrics and statistics
        """
        total_alerts = len(self.alerts)
        open_alerts = len([a for a in self.alerts if a["status"] == "open"])
        critical_alerts = len(
            [a for a in self.alerts if a["threat_level"] == ThreatLevel.CRITICAL.value]
        )

        return {
            "total_alerts": total_alerts,
            "open_alerts": open_alerts,
            "critical_alerts": critical_alerts,
            "blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "failed_login_users": len(self.failed_login_attempts),
            "rate_violations": len(self.rate_violations),
        }

    def generate_security_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate security report for time period
        """
        # Filter alerts by date
        period_alerts = [
            a
            for a in self.alerts
            if start_date <= datetime.fromisoformat(a["timestamp"]) <= end_date
        ]

        # Calculate metrics
        total_alerts = len(period_alerts)
        by_threat_level = defaultdict(int)
        by_event_type = defaultdict(int)

        for alert in period_alerts:
            by_threat_level[alert["threat_level"]] += 1
            by_event_type[alert["event_type"]] += 1

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_alerts": total_alerts,
                "by_threat_level": dict(by_threat_level),
                "by_event_type": dict(by_event_type),
            },
            "top_threats": self._get_top_threats(period_alerts),
            "recommendations": self._generate_security_recommendations(),
        }

    def _get_top_threats(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get top security threats
        """
        threat_counts = defaultdict(int)

        for alert in alerts:
            threat_counts[alert["event_type"]] += 1

        sorted_threats = sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)

        return [
            {"threat": threat, "count": count} for threat, count in sorted_threats[:5]
        ]

    def _generate_security_recommendations(self) -> List[str]:
        """
        Generate security recommendations
        """
        recommendations = []

        if len(self.blocked_ips) > 10:
            recommendations.append("Review and update IP blocklist")

        if len(self.failed_login_attempts) > 5:
            recommendations.append("Implement stronger password policies")

        if len(self.alerts) > 100:
            recommendations.append("Review and tune security monitoring rules")

        recommendations.extend(
            [
                "Conduct regular security audits",
                "Update security policies and procedures",
                "Provide security awareness training",
                "Review access control policies",
            ]
        )

        return recommendations


# Global security monitor instance
security_monitor = SecurityMonitor()
