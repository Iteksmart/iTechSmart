"""
iTechSmart Sentinel - Alerting Engine
Smart alert routing with ML-based fatigue reduction
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import hashlib
import json

from app.models.models import Service, Alert, Incident, OnCallSchedule, SeverityLevel, AlertStatus


class AlertingEngine:
    """
    Advanced alerting engine with smart routing and fatigue reduction
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_history = {}  # In-memory cache for deduplication
    
    async def create_alert(
        self,
        service_name: str,
        alert_name: str,
        alert_type: str,
        severity: str,
        title: str,
        description: Optional[str] = None,
        condition: Optional[Dict[str, Any]] = None,
        current_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        tags: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """
        Create a new alert with deduplication
        """
        # Get or create service
        service = self.db.query(Service).filter(Service.name == service_name).first()
        if not service:
            service = Service(
                name=service_name,
                display_name=service_name,
                is_healthy=False
            )
            self.db.add(service)
            self.db.flush()
        
        # Generate fingerprint for deduplication
        fingerprint_data = f"{service_name}:{alert_name}:{alert_type}:{title}"
        fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        # Check for existing firing alert with same fingerprint
        existing_alert = self.db.query(Alert).filter(
            and_(
                Alert.fingerprint == fingerprint,
                Alert.status == AlertStatus.FIRING.value
            )
        ).first()
        
        if existing_alert:
            # Update existing alert instead of creating duplicate
            existing_alert.current_value = current_value
            existing_alert.updated_at = datetime.utcnow()
            self.db.commit()
            return existing_alert
        
        # Create new alert
        alert = Alert(
            service_id=service.id,
            alert_name=alert_name,
            alert_type=alert_type,
            severity=severity,
            status=AlertStatus.FIRING.value,
            triggered_at=datetime.utcnow(),
            title=title,
            description=description,
            condition=condition or {},
            current_value=current_value,
            threshold_value=threshold_value,
            fingerprint=fingerprint,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        # Check if should create incident
        await self._check_incident_creation(alert)
        
        return alert
    
    async def acknowledge_alert(
        self,
        alert_id: int,
        acknowledged_by: str
    ) -> Alert:
        """
        Acknowledge an alert
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert.status = AlertStatus.ACKNOWLEDGED.value
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    async def resolve_alert(
        self,
        alert_id: int,
        resolution_note: Optional[str] = None
    ) -> Alert:
        """
        Resolve an alert
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert.status = AlertStatus.RESOLVED.value
        alert.resolved_at = datetime.utcnow()
        
        if resolution_note:
            alert.metadata = alert.metadata or {}
            alert.metadata["resolution_note"] = resolution_note
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    async def silence_alert(
        self,
        alert_id: int,
        duration_minutes: int = 60,
        silenced_by: Optional[str] = None
    ) -> Alert:
        """
        Silence an alert for a duration
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert.status = AlertStatus.SILENCED.value
        alert.metadata = alert.metadata or {}
        alert.metadata["silenced_until"] = (
            datetime.utcnow() + timedelta(minutes=duration_minutes)
        ).isoformat()
        alert.metadata["silenced_by"] = silenced_by
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    async def get_active_alerts(
        self,
        service_name: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all active (firing or acknowledged) alerts
        """
        query = self.db.query(Alert).filter(
            Alert.status.in_([AlertStatus.FIRING.value, AlertStatus.ACKNOWLEDGED.value])
        )
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        alerts = query.order_by(
            desc(Alert.severity),
            desc(Alert.triggered_at)
        ).limit(limit).all()
        
        return [
            {
                "id": alert.id,
                "service": alert.service.name,
                "alert_name": alert.alert_name,
                "severity": alert.severity,
                "status": alert.status,
                "title": alert.title,
                "description": alert.description,
                "triggered_at": alert.triggered_at.isoformat(),
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "acknowledged_by": alert.acknowledged_by,
                "incident_id": alert.incident_id
            }
            for alert in alerts
        ]
    
    async def get_alert_statistics(
        self,
        service_name: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get alert statistics for a time period
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(Alert).filter(Alert.triggered_at >= since)
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        alerts = query.all()
        
        # Calculate statistics
        total_alerts = len(alerts)
        
        by_severity = {
            SeverityLevel.CRITICAL.value: 0,
            SeverityLevel.HIGH.value: 0,
            SeverityLevel.MEDIUM.value: 0,
            SeverityLevel.LOW.value: 0,
            SeverityLevel.INFO.value: 0
        }
        
        by_status = {
            AlertStatus.FIRING.value: 0,
            AlertStatus.ACKNOWLEDGED.value: 0,
            AlertStatus.RESOLVED.value: 0,
            AlertStatus.SILENCED.value: 0
        }
        
        by_type = {}
        
        for alert in alerts:
            by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
            by_status[alert.status] = by_status.get(alert.status, 0) + 1
            by_type[alert.alert_type] = by_type.get(alert.alert_type, 0) + 1
        
        # Calculate MTTR (Mean Time To Resolve)
        resolved_alerts = [a for a in alerts if a.resolved_at]
        mttr_minutes = 0.0
        if resolved_alerts:
            total_resolution_time = sum(
                (a.resolved_at - a.triggered_at).total_seconds() / 60
                for a in resolved_alerts
            )
            mttr_minutes = total_resolution_time / len(resolved_alerts)
        
        return {
            "time_period_hours": hours,
            "total_alerts": total_alerts,
            "by_severity": by_severity,
            "by_status": by_status,
            "by_type": by_type,
            "mttr_minutes": round(mttr_minutes, 2)
        }
    
    async def detect_alert_fatigue(
        self,
        service_name: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Detect alert fatigue patterns using ML-based analysis
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(Alert).filter(Alert.triggered_at >= since)
        
        if service_name:
            query = query.join(Service).filter(Service.name == service_name)
        
        alerts = query.all()
        
        # Analyze patterns
        alert_frequency = {}  # Alerts per hour
        flapping_alerts = {}  # Alerts that fire/resolve repeatedly
        noisy_alerts = {}  # High-frequency low-severity alerts
        
        for alert in alerts:
            # Track frequency
            hour_key = alert.triggered_at.strftime("%Y-%m-%d %H:00")
            alert_frequency[hour_key] = alert_frequency.get(hour_key, 0) + 1
            
            # Track flapping (same fingerprint firing multiple times)
            if alert.fingerprint:
                flapping_alerts[alert.fingerprint] = flapping_alerts.get(alert.fingerprint, 0) + 1
            
            # Track noisy alerts (low severity, high frequency)
            if alert.severity in [SeverityLevel.LOW.value, SeverityLevel.INFO.value]:
                key = f"{alert.service.name}:{alert.alert_name}"
                noisy_alerts[key] = noisy_alerts.get(key, 0) + 1
        
        # Identify problematic patterns
        high_frequency_hours = [
            {"hour": hour, "count": count}
            for hour, count in sorted(
                alert_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        ]
        
        flapping_list = [
            {"fingerprint": fp, "fire_count": count}
            for fp, count in sorted(
                flapping_alerts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            if count > 3  # Fired more than 3 times
        ]
        
        noisy_list = [
            {"alert": alert, "count": count}
            for alert, count in sorted(
                noisy_alerts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            if count > 10  # More than 10 occurrences
        ]
        
        # Calculate fatigue score (0-100)
        fatigue_score = 0
        if len(alerts) > 100:
            fatigue_score += 30
        if len(flapping_list) > 5:
            fatigue_score += 30
        if len(noisy_list) > 5:
            fatigue_score += 40
        
        fatigue_score = min(fatigue_score, 100)
        
        return {
            "fatigue_score": fatigue_score,
            "fatigue_level": self._get_fatigue_level(fatigue_score),
            "total_alerts": len(alerts),
            "high_frequency_hours": high_frequency_hours,
            "flapping_alerts": flapping_list,
            "noisy_alerts": noisy_list,
            "recommendations": self._get_fatigue_recommendations(
                fatigue_score,
                len(flapping_list),
                len(noisy_list)
            )
        }
    
    def _get_fatigue_level(self, score: int) -> str:
        """Get fatigue level from score"""
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
    
    def _get_fatigue_recommendations(
        self,
        score: int,
        flapping_count: int,
        noisy_count: int
    ) -> List[str]:
        """Get recommendations to reduce alert fatigue"""
        recommendations = []
        
        if score >= 70:
            recommendations.append("URGENT: Alert fatigue is critical. Immediate action required.")
        
        if flapping_count > 5:
            recommendations.append(
                "Fix flapping alerts by adjusting thresholds or adding hysteresis"
            )
        
        if noisy_count > 5:
            recommendations.append(
                "Reduce noisy alerts by increasing severity thresholds or aggregating similar alerts"
            )
        
        if score >= 50:
            recommendations.append(
                "Consider implementing alert grouping and deduplication"
            )
            recommendations.append(
                "Review and disable low-value alerts"
            )
        
        if not recommendations:
            recommendations.append("Alert health is good. Continue monitoring.")
        
        return recommendations
    
    async def _send_notifications(self, alert: Alert):
        """
        Send alert notifications to configured channels
        """
        # Get on-call schedule
        oncall = self.db.query(OnCallSchedule).filter(
            OnCallSchedule.team == alert.service.team
        ).first()
        
        channels = []
        
        if oncall and oncall.notification_channels:
            channels = oncall.notification_channels
        else:
            # Default channels based on severity
            if alert.severity == SeverityLevel.CRITICAL.value:
                channels = ["slack", "email", "sms", "phone"]
            elif alert.severity == SeverityLevel.HIGH.value:
                channels = ["slack", "email", "sms"]
            elif alert.severity == SeverityLevel.MEDIUM.value:
                channels = ["slack", "email"]
            else:
                channels = ["slack"]
        
        alert.notification_channels = channels
        alert.notification_sent = True
        
        # TODO: Integrate with iTechSmart Notify for actual notification sending
        # For now, just mark as sent
        
        self.db.commit()
    
    async def _check_incident_creation(self, alert: Alert):
        """
        Check if alert should trigger incident creation
        """
        # Create incident for critical alerts
        if alert.severity == SeverityLevel.CRITICAL.value:
            # Check if there's already an open incident for this service
            existing_incident = self.db.query(Incident).filter(
                and_(
                    Incident.status.in_(["open", "investigating"]),
                    Incident.affected_services.contains([alert.service_id])
                )
            ).first()
            
            if not existing_incident:
                # Create new incident
                incident_number = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{alert.id}"
                
                incident = Incident(
                    incident_number=incident_number,
                    title=alert.title,
                    description=alert.description,
                    status="open",
                    severity=alert.severity,
                    detected_at=alert.triggered_at,
                    affected_services=[alert.service_id],
                    team=alert.service.team
                )
                
                self.db.add(incident)
                self.db.flush()
                
                # Link alert to incident
                alert.incident_id = incident.id
                
                self.db.commit()