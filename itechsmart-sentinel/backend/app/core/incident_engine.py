"""
iTechSmart Sentinel - Incident Management Engine
Automated incident creation, runbooks, and post-mortems
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.models import (
    Incident,
    IncidentUpdate,
    Alert,
    Service,
    Runbook,
    RunbookExecution,
    IncidentStatus,
    SeverityLevel,
)


class IncidentEngine:
    """
    Comprehensive incident management with automation
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_incident(
        self,
        title: str,
        description: Optional[str] = None,
        severity: str = SeverityLevel.MEDIUM.value,
        affected_services: Optional[List[int]] = None,
        team: Optional[str] = None,
        assigned_to: Optional[str] = None,
        alert_ids: Optional[List[int]] = None,
    ) -> Incident:
        """
        Create a new incident
        """
        # Generate incident number
        today = datetime.utcnow().strftime("%Y%m%d")
        count = (
            self.db.query(Incident)
            .filter(Incident.incident_number.like(f"INC-{today}-%"))
            .count()
        )
        incident_number = f"INC-{today}-{count + 1:04d}"

        # Create incident
        incident = Incident(
            incident_number=incident_number,
            title=title,
            description=description,
            status=IncidentStatus.OPEN.value,
            severity=severity,
            detected_at=datetime.utcnow(),
            affected_services=affected_services or [],
            team=team,
            assigned_to=assigned_to,
        )

        self.db.add(incident)
        self.db.flush()

        # Link alerts to incident
        if alert_ids:
            for alert_id in alert_ids:
                alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
                if alert:
                    alert.incident_id = incident.id

        # Add initial update
        initial_update = IncidentUpdate(
            incident_id=incident.id,
            update_type="created",
            message=f"Incident created: {title}",
            author="system",
        )
        self.db.add(initial_update)

        self.db.commit()
        self.db.refresh(incident)

        # Check for applicable runbooks
        await self._execute_applicable_runbooks(incident)

        return incident

    async def update_incident_status(
        self,
        incident_id: int,
        new_status: str,
        author: str,
        message: Optional[str] = None,
    ) -> Incident:
        """
        Update incident status
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        old_status = incident.status
        incident.status = new_status

        # Update timestamps
        now = datetime.utcnow()
        if (
            new_status == IncidentStatus.INVESTIGATING.value
            and not incident.acknowledged_at
        ):
            incident.acknowledged_at = now
            incident.time_to_acknowledge_minutes = (
                now - incident.detected_at
            ).total_seconds() / 60
        elif new_status == IncidentStatus.RESOLVED.value and not incident.resolved_at:
            incident.resolved_at = now
            incident.time_to_resolve_minutes = (
                now - incident.detected_at
            ).total_seconds() / 60
        elif new_status == IncidentStatus.CLOSED.value and not incident.closed_at:
            incident.closed_at = now

        # Add status update
        update_message = message or f"Status changed from {old_status} to {new_status}"
        update = IncidentUpdate(
            incident_id=incident.id,
            update_type="status_change",
            message=update_message,
            author=author,
        )
        self.db.add(update)

        self.db.commit()
        self.db.refresh(incident)

        return incident

    async def add_incident_update(
        self,
        incident_id: int,
        update_type: str,
        message: str,
        author: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IncidentUpdate:
        """
        Add an update to an incident
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        update = IncidentUpdate(
            incident_id=incident_id,
            update_type=update_type,
            message=message,
            author=author,
            metadata=metadata or {},
        )

        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)

        return update

    async def assign_incident(
        self, incident_id: int, assigned_to: str, author: str
    ) -> Incident:
        """
        Assign incident to a person
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        old_assignee = incident.assigned_to
        incident.assigned_to = assigned_to

        # Add update
        message = f"Incident assigned to {assigned_to}"
        if old_assignee:
            message += f" (previously: {old_assignee})"

        update = IncidentUpdate(
            incident_id=incident_id,
            update_type="assignment",
            message=message,
            author=author,
        )
        self.db.add(update)

        self.db.commit()
        self.db.refresh(incident)

        return incident

    async def add_root_cause(
        self, incident_id: int, root_cause: str, resolution_summary: str, author: str
    ) -> Incident:
        """
        Add root cause analysis and resolution
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.root_cause = root_cause
        incident.resolution_summary = resolution_summary

        # Add update
        update = IncidentUpdate(
            incident_id=incident_id,
            update_type="resolution",
            message=f"Root cause identified: {root_cause[:100]}...",
            author=author,
        )
        self.db.add(update)

        self.db.commit()
        self.db.refresh(incident)

        return incident

    async def get_active_incidents(
        self,
        severity: Optional[str] = None,
        team: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all active incidents
        """
        query = self.db.query(Incident).filter(
            Incident.status.in_(
                [
                    IncidentStatus.OPEN.value,
                    IncidentStatus.INVESTIGATING.value,
                    IncidentStatus.IDENTIFIED.value,
                    IncidentStatus.MONITORING.value,
                ]
            )
        )

        if severity:
            query = query.filter(Incident.severity == severity)

        if team:
            query = query.filter(Incident.team == team)

        if assigned_to:
            query = query.filter(Incident.assigned_to == assigned_to)

        incidents = query.order_by(
            desc(Incident.severity), desc(Incident.detected_at)
        ).all()

        return [
            {
                "id": inc.id,
                "incident_number": inc.incident_number,
                "title": inc.title,
                "status": inc.status,
                "severity": inc.severity,
                "detected_at": inc.detected_at.isoformat(),
                "assigned_to": inc.assigned_to,
                "team": inc.team,
                "affected_services": inc.affected_services,
                "alert_count": len(inc.alerts),
            }
            for inc in incidents
        ]

    async def get_incident_timeline(self, incident_id: int) -> Dict[str, Any]:
        """
        Get complete incident timeline with all updates
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        updates = (
            self.db.query(IncidentUpdate)
            .filter(IncidentUpdate.incident_id == incident_id)
            .order_by(IncidentUpdate.created_at)
            .all()
        )

        return {
            "incident": {
                "id": incident.id,
                "incident_number": incident.incident_number,
                "title": incident.title,
                "description": incident.description,
                "status": incident.status,
                "severity": incident.severity,
                "detected_at": incident.detected_at.isoformat(),
                "resolved_at": (
                    incident.resolved_at.isoformat() if incident.resolved_at else None
                ),
                "assigned_to": incident.assigned_to,
                "team": incident.team,
                "root_cause": incident.root_cause,
                "resolution_summary": incident.resolution_summary,
            },
            "timeline": [
                {
                    "id": update.id,
                    "update_type": update.update_type,
                    "message": update.message,
                    "author": update.author,
                    "created_at": update.created_at.isoformat(),
                }
                for update in updates
            ],
            "alerts": [
                {
                    "id": alert.id,
                    "alert_name": alert.alert_name,
                    "severity": alert.severity,
                    "triggered_at": alert.triggered_at.isoformat(),
                }
                for alert in incident.alerts
            ],
        }

    async def get_incident_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get incident statistics
        """
        since = datetime.utcnow() - timedelta(days=days)

        incidents = self.db.query(Incident).filter(Incident.detected_at >= since).all()

        total_incidents = len(incidents)

        by_severity = {
            SeverityLevel.CRITICAL.value: 0,
            SeverityLevel.HIGH.value: 0,
            SeverityLevel.MEDIUM.value: 0,
            SeverityLevel.LOW.value: 0,
        }

        by_status = {
            IncidentStatus.OPEN.value: 0,
            IncidentStatus.INVESTIGATING.value: 0,
            IncidentStatus.IDENTIFIED.value: 0,
            IncidentStatus.MONITORING.value: 0,
            IncidentStatus.RESOLVED.value: 0,
            IncidentStatus.CLOSED.value: 0,
        }

        for incident in incidents:
            by_severity[incident.severity] = by_severity.get(incident.severity, 0) + 1
            by_status[incident.status] = by_status.get(incident.status, 0) + 1

        # Calculate MTTR (Mean Time To Resolve)
        resolved_incidents = [i for i in incidents if i.time_to_resolve_minutes]
        mttr_minutes = 0.0
        if resolved_incidents:
            mttr_minutes = sum(
                i.time_to_resolve_minutes for i in resolved_incidents
            ) / len(resolved_incidents)

        # Calculate MTTA (Mean Time To Acknowledge)
        acknowledged_incidents = [i for i in incidents if i.time_to_acknowledge_minutes]
        mtta_minutes = 0.0
        if acknowledged_incidents:
            mtta_minutes = sum(
                i.time_to_acknowledge_minutes for i in acknowledged_incidents
            ) / len(acknowledged_incidents)

        return {
            "time_period_days": days,
            "total_incidents": total_incidents,
            "by_severity": by_severity,
            "by_status": by_status,
            "mttr_minutes": round(mttr_minutes, 2),
            "mtta_minutes": round(mtta_minutes, 2),
            "resolved_count": len(resolved_incidents),
            "resolution_rate": round(
                (
                    (len(resolved_incidents) / total_incidents * 100)
                    if total_incidents > 0
                    else 0.0
                ),
                2,
            ),
        }

    async def generate_post_mortem(self, incident_id: int) -> Dict[str, Any]:
        """
        Generate post-mortem template
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Get timeline
        updates = (
            self.db.query(IncidentUpdate)
            .filter(IncidentUpdate.incident_id == incident_id)
            .order_by(IncidentUpdate.created_at)
            .all()
        )

        # Calculate impact duration
        impact_duration = None
        if incident.resolved_at:
            impact_duration = (
                incident.resolved_at - incident.detected_at
            ).total_seconds() / 60

        return {
            "incident_number": incident.incident_number,
            "title": incident.title,
            "date": incident.detected_at.strftime("%Y-%m-%d"),
            "severity": incident.severity,
            "impact_duration_minutes": (
                round(impact_duration, 2) if impact_duration else None
            ),
            "summary": incident.description,
            "timeline": [
                {
                    "time": update.created_at.strftime("%H:%M:%S"),
                    "event": update.message,
                }
                for update in updates
            ],
            "root_cause": incident.root_cause or "To be determined",
            "resolution": incident.resolution_summary or "To be determined",
            "lessons_learned": incident.lessons_learned or "To be documented",
            "action_items": incident.action_items or [],
            "affected_services": incident.affected_services,
            "team": incident.team,
        }

    async def _execute_applicable_runbooks(self, incident: Incident):
        """
        Execute runbooks that match incident conditions
        """
        # Get all automated runbooks
        runbooks = (
            self.db.query(Runbook)
            .filter(
                and_(Runbook.trigger_type == "incident", Runbook.is_automated == True)
            )
            .all()
        )

        for runbook in runbooks:
            # Check if conditions match
            if self._check_runbook_conditions(runbook, incident):
                # Execute runbook
                await self._execute_runbook(runbook, incident)

    def _check_runbook_conditions(self, runbook: Runbook, incident: Incident) -> bool:
        """
        Check if runbook conditions match incident
        """
        conditions = runbook.trigger_conditions or {}

        # Check severity
        if "severity" in conditions:
            if incident.severity not in conditions["severity"]:
                return False

        # Check affected services
        if "services" in conditions:
            if not any(s in incident.affected_services for s in conditions["services"]):
                return False

        return True

    async def _execute_runbook(self, runbook: Runbook, incident: Incident):
        """
        Execute a runbook
        """
        execution = RunbookExecution(
            runbook_id=runbook.id,
            started_at=datetime.utcnow(),
            status="running",
            triggered_by="system",
            trigger_reason=f"Incident {incident.incident_number}",
        )

        self.db.add(execution)
        self.db.commit()

        # TODO: Implement actual runbook step execution
        # For now, just mark as completed
        execution.status = "success"
        execution.completed_at = datetime.utcnow()
        execution.duration_seconds = (
            execution.completed_at - execution.started_at
        ).total_seconds()

        self.db.commit()
