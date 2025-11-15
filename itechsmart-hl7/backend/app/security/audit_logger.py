"""
Enhanced Audit Logger
HIPAA-compliant audit logging with database integration
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from ..database.models import AuditLog
from ..database.session import get_db
from .hipaa_compliance import HIPAAEventType

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Enhanced audit logger with database persistence
    """
    
    def __init__(self):
        self.in_memory_logs = []
    
    def log_event(
        self,
        event_type: str,
        event_category: str,
        action: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        patient_mrn: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        status: str = "success",
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log an audit event to database
        """
        try:
            # Create audit log entry
            audit_entry = AuditLog(
                event_type=event_type,
                event_category=event_category,
                action=action,
                user_id=user_id,
                username=username,
                user_role=user_role,
                resource_type=resource_type,
                resource_id=resource_id,
                patient_id=patient_id,
                patient_mrn=patient_mrn,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                status=status,
                status_code=status_code,
                error_message=error_message,
                details=details,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms
            )
            
            # Save to database if session provided
            if db:
                db.add(audit_entry)
                db.commit()
                db.refresh(audit_entry)
            else:
                # Store in memory if no DB session
                self.in_memory_logs.append(audit_entry.__dict__)
            
            return audit_entry
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Store in memory as fallback
            self.in_memory_logs.append({
                'event_type': event_type,
                'action': action,
                'username': username,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            })
            raise
    
    def log_phi_access(
        self,
        user_id: str,
        username: str,
        patient_id: str,
        patient_mrn: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log PHI (Protected Health Information) access
        """
        return self.log_event(
            event_type=HIPAAEventType.PHI_ACCESS.value,
            event_category="phi_access",
            action=action,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            patient_mrn=patient_mrn,
            ip_address=ip_address,
            status="success" if success else "failure",
            db=db
        )
    
    def log_authentication(
        self,
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log authentication attempt
        """
        return self.log_event(
            event_type=HIPAAEventType.AUTHENTICATION.value,
            event_category="authentication",
            action="login_attempt",
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure",
            error_message=error_message,
            db=db
        )
    
    def log_data_modification(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        resource_id: str,
        action: str,
        patient_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log data modification
        """
        return self.log_event(
            event_type=HIPAAEventType.PHI_MODIFICATION.value,
            event_category="data_modification",
            action=action,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            details={'changes': changes} if changes else None,
            status="success",
            db=db
        )
    
    def log_data_export(
        self,
        user_id: str,
        username: str,
        resource_type: str,
        record_count: int,
        export_format: str,
        patient_ids: Optional[List[str]] = None,
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log data export
        """
        return self.log_event(
            event_type=HIPAAEventType.PHI_EXPORT.value,
            event_category="data_export",
            action="export_data",
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            details={
                'record_count': record_count,
                'export_format': export_format,
                'patient_ids': patient_ids
            },
            status="success",
            db=db
        )
    
    def log_security_incident(
        self,
        incident_type: str,
        description: str,
        severity: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log security incident
        """
        return self.log_event(
            event_type=HIPAAEventType.SECURITY_INCIDENT.value,
            event_category="security",
            action=incident_type,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            status="incident",
            error_message=description,
            details={
                'severity': severity,
                **(details or {})
            },
            db=db
        )
    
    def log_configuration_change(
        self,
        user_id: str,
        username: str,
        config_type: str,
        changes: Dict[str, Any],
        db: Optional[Session] = None
    ) -> AuditLog:
        """
        Log system configuration change
        """
        return self.log_event(
            event_type=HIPAAEventType.CONFIGURATION_CHANGE.value,
            event_category="configuration",
            action="config_change",
            user_id=user_id,
            username=username,
            resource_type=config_type,
            details={'changes': changes},
            status="success",
            db=db
        )
    
    def get_audit_trail(
        self,
        patient_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        db: Optional[Session] = None
    ) -> List[AuditLog]:
        """
        Retrieve audit trail with filters
        """
        if not db:
            return self.in_memory_logs[:limit]
        
        query = db.query(AuditLog)
        
        if patient_id:
            query = query.filter(AuditLog.patient_id == patient_id)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit)
        
        return query.all()
    
    def get_patient_access_history(
        self,
        patient_id: str,
        days: int = 30,
        db: Optional[Session] = None
    ) -> List[AuditLog]:
        """
        Get complete access history for a patient
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return self.get_audit_trail(
            patient_id=patient_id,
            start_date=start_date,
            db=db
        )
    
    def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
        db: Optional[Session] = None
    ) -> List[AuditLog]:
        """
        Get user activity history
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return self.get_audit_trail(
            user_id=user_id,
            start_date=start_date,
            db=db
        )
    
    def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit report
        """
        logs = self.get_audit_trail(
            start_date=start_date,
            end_date=end_date,
            limit=10000,
            db=db
        )
        
        total_events = len(logs)
        event_types = {}
        users = set()
        patients = set()
        failed_events = 0
        
        for log in logs:
            event_type = log.event_type if hasattr(log, 'event_type') else log.get('event_type')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            username = log.username if hasattr(log, 'username') else log.get('username')
            if username:
                users.add(username)
            
            patient_id = log.patient_id if hasattr(log, 'patient_id') else log.get('patient_id')
            if patient_id:
                patients.add(patient_id)
            
            status = log.status if hasattr(log, 'status') else log.get('status')
            if status in ['failure', 'error']:
                failed_events += 1
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': total_events,
                'unique_users': len(users),
                'unique_patients': len(patients),
                'failed_events': failed_events,
                'success_rate': ((total_events - failed_events) / total_events * 100) if total_events > 0 else 100
            },
            'event_types': event_types
        }


audit_logger = AuditLogger()