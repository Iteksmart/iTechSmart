"""
iTechSmart HL7 - Auto-Remediation API Endpoints
REST API for autonomous self-healing capabilities
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.core.auto_remediation import (
    HL7AutoRemediationEngine,
    RemediationMode,
    HL7Issue,
    RemediationAction,
    IssueType,
    IssueSeverity
)
from app.core.message_retry import MessageRetrySystem, HL7Message, MessageStatus, RetryPolicy
from app.core.service_manager import ServiceHealthManager, ServiceConfig, ServiceType
from app.monitoring.message_queue_monitor import MessageQueueMonitor

router = APIRouter(prefix="/api/v1/remediation", tags=["Auto-Remediation"])

# Global instances (in production, use dependency injection)
remediation_engine = HL7AutoRemediationEngine()
retry_system = MessageRetrySystem()
service_manager = ServiceHealthManager()
queue_monitor = MessageQueueMonitor()


# Request/Response Models
class AlertRequest(BaseModel):
    """Alert submission request"""
    type: str
    severity: str
    description: str
    system: str
    symptoms: List[str] = []
    metrics: Dict[str, Any] = {}


class IssueResponse(BaseModel):
    """Issue response"""
    issue_id: str
    issue_type: str
    severity: str
    description: str
    affected_system: str
    detected_at: str
    root_cause: Optional[str] = None
    recommended_actions: List[str] = []


class ActionApprovalRequest(BaseModel):
    """Action approval request"""
    action_id: str
    approved: bool
    reason: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    """Configuration update request"""
    mode: Optional[str] = None
    approval_timeout: Optional[int] = None
    max_retries: Optional[int] = None


# Auto-Remediation Endpoints

@router.post("/alerts", response_model=IssueResponse)
async def submit_alert(alert: AlertRequest):
    """
    Submit an alert for autonomous remediation
    
    The system will:
    1. Detect and classify the issue
    2. Perform AI-powered diagnosis
    3. Generate remediation actions
    4. Execute actions (with approval if needed)
    """
    try:
        # Convert to alert dict
        alert_dict = alert.dict()
        
        # Detect issue
        issue = await remediation_engine.detect_issue(alert_dict)
        if not issue:
            raise HTTPException(status_code=400, detail="Unable to detect issue from alert")
        
        # Diagnose issue
        issue = await remediation_engine.diagnose(issue)
        
        # Attempt remediation
        success = await remediation_engine.remediate(issue)
        
        return IssueResponse(
            issue_id=issue.issue_id,
            issue_type=issue.issue_type.value,
            severity=issue.severity.value,
            description=issue.description,
            affected_system=issue.affected_system,
            detected_at=issue.detected_at.isoformat(),
            root_cause=issue.root_cause,
            recommended_actions=issue.recommended_actions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/issues")
async def get_issues(limit: int = 100):
    """Get recent issues"""
    # In production, retrieve from database
    return {
        "issues": [],
        "total": 0
    }


@router.get("/actions/pending")
async def get_pending_actions():
    """Get actions pending approval"""
    pending = remediation_engine.get_pending_approvals()
    return {
        "pending_actions": [
            {
                "action_id": a.action_id,
                "issue_id": a.issue_id,
                "action_type": a.action_type,
                "description": a.description,
                "risk_level": a.risk_level,
                "created_at": a.created_at.isoformat()
            }
            for a in pending
        ],
        "count": len(pending)
    }


@router.post("/actions/approve")
async def approve_action(request: ActionApprovalRequest):
    """Approve or reject a pending action"""
    if request.approved:
        success = remediation_engine.approve_action(request.action_id)
        if success:
            return {"message": "Action approved", "action_id": request.action_id}
    else:
        success = remediation_engine.reject_action(request.action_id, request.reason or "")
        if success:
            return {"message": "Action rejected", "action_id": request.action_id}
    
    raise HTTPException(status_code=404, detail="Action not found")


@router.get("/actions/history")
async def get_action_history(limit: int = 100):
    """Get action execution history"""
    history = remediation_engine.get_action_history(limit)
    return {
        "actions": [
            {
                "action_id": a.action_id,
                "issue_id": a.issue_id,
                "action_type": a.action_type,
                "status": a.status,
                "executed_at": a.executed_at.isoformat() if a.executed_at else None,
                "result": a.result
            }
            for a in history
        ],
        "count": len(history)
    }


@router.get("/statistics")
async def get_statistics():
    """Get remediation statistics"""
    return remediation_engine.get_statistics()


@router.post("/config")
async def update_config(config: ConfigUpdateRequest):
    """Update remediation configuration"""
    if config.mode:
        remediation_engine.mode = RemediationMode(config.mode)
    if config.approval_timeout:
        remediation_engine.approval_timeout = config.approval_timeout
    if config.max_retries:
        remediation_engine.max_retries = config.max_retries
    
    return {"message": "Configuration updated"}


@router.post("/kill-switch/enable")
async def enable_kill_switch():
    """Enable global kill switch - stops all automation"""
    remediation_engine.enable_kill_switch()
    return {"message": "Kill switch enabled", "status": "automation_stopped"}


@router.post("/kill-switch/disable")
async def disable_kill_switch():
    """Disable global kill switch - resumes automation"""
    remediation_engine.disable_kill_switch()
    return {"message": "Kill switch disabled", "status": "automation_resumed"}


# Message Retry Endpoints

@router.post("/messages/submit")
async def submit_message(message: Dict[str, Any]):
    """Submit a message for delivery with automatic retry"""
    try:
        hl7_message = HL7Message(**message)
        message_id = await retry_system.submit_message(hl7_message)
        return {"message_id": message_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/messages/{message_id}/status")
async def get_message_status(message_id: str):
    """Get status of a message"""
    status = retry_system.get_message_status(message_id)
    if not status:
        raise HTTPException(status_code=404, detail="Message not found")
    return status


@router.get("/messages/retry-queue")
async def get_retry_queue(limit: int = 100):
    """Get messages in retry queue"""
    messages = retry_system.get_retry_queue(limit)
    return {
        "messages": [
            {
                "message_id": m.message_id,
                "status": m.status,
                "retry_count": m.retry_count,
                "next_retry_at": m.next_retry_at.isoformat() if m.next_retry_at else None
            }
            for m in messages
        ],
        "count": len(messages)
    }


@router.get("/messages/dead-letter")
async def get_dead_letter_queue(limit: int = 100):
    """Get messages in dead letter queue"""
    messages = retry_system.get_dead_letter_queue(limit)
    return {
        "messages": [
            {
                "message_id": m.message_id,
                "status": m.status,
                "retry_count": m.retry_count,
                "last_error": m.last_error
            }
            for m in messages
        ],
        "count": len(messages)
    }


@router.post("/messages/{message_id}/retry")
async def retry_dead_letter_message(message_id: str):
    """Manually retry a message from dead letter queue"""
    success = await retry_system.retry_dead_letter_message(message_id)
    if success:
        return {"message": "Message moved to retry queue", "message_id": message_id}
    raise HTTPException(status_code=404, detail="Message not found in dead letter queue")


@router.get("/messages/statistics")
async def get_retry_statistics():
    """Get message retry statistics"""
    return retry_system.get_statistics()


# Service Management Endpoints

@router.post("/services/register")
async def register_service(config: Dict[str, Any]):
    """Register a service for health monitoring"""
    try:
        service_config = ServiceConfig(**config)
        service_manager.register_service(service_config)
        return {"message": "Service registered", "service_name": service_config.service_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/services")
async def get_all_services():
    """Get all registered services and their status"""
    status = service_manager.get_all_service_status()
    return {
        "services": [
            {
                "service_name": s.service_name,
                "status": s.status,
                "response_time": s.response_time,
                "checked_at": s.checked_at.isoformat(),
                "error": s.error
            }
            for s in status.values()
        ],
        "count": len(status)
    }


@router.get("/services/{service_name}/status")
async def get_service_status(service_name: str):
    """Get health status of a specific service"""
    status = service_manager.get_service_status(service_name)
    if not status:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return {
        "service_name": status.service_name,
        "status": status.status,
        "response_time": status.response_time,
        "checked_at": status.checked_at.isoformat(),
        "error": status.error,
        "metrics": status.metrics
    }


@router.post("/services/{service_name}/restart")
async def restart_service(service_name: str):
    """Manually restart a service"""
    success = await service_manager.restart_service(service_name)
    if success:
        return {"message": "Service restarted successfully", "service_name": service_name}
    raise HTTPException(status_code=500, detail="Failed to restart service")


@router.get("/services/{service_name}/history")
async def get_service_history(service_name: str, limit: int = 100):
    """Get health check history for a service"""
    history = service_manager.get_service_health_history(service_name, limit)
    return {
        "history": [
            {
                "status": h.status,
                "response_time": h.response_time,
                "checked_at": h.checked_at.isoformat(),
                "error": h.error
            }
            for h in history
        ],
        "count": len(history)
    }


@router.get("/services/statistics")
async def get_service_statistics():
    """Get service management statistics"""
    return service_manager.get_statistics()


# Queue Monitoring Endpoints

@router.post("/queues/register")
async def register_queue(queue_name: str, config: Optional[Dict[str, Any]] = None):
    """Register a queue for monitoring"""
    queue_monitor.register_queue(queue_name, config)
    return {"message": "Queue registered", "queue_name": queue_name}


@router.get("/queues")
async def get_all_queues():
    """Get metrics for all monitored queues"""
    metrics = queue_monitor.get_all_queue_metrics()
    return {
        "queues": [
            {
                "queue_name": m.queue_name,
                "queue_depth": m.queue_depth,
                "messages_per_second": m.messages_per_second,
                "status": m.status,
                "timestamp": m.timestamp.isoformat()
            }
            for m in metrics.values()
        ],
        "count": len(metrics)
    }


@router.get("/queues/{queue_name}/metrics")
async def get_queue_metrics(queue_name: str):
    """Get current metrics for a queue"""
    metrics = queue_monitor.get_queue_metrics(queue_name)
    if not metrics:
        raise HTTPException(status_code=404, detail="Queue not found")
    
    return {
        "queue_name": metrics.queue_name,
        "queue_depth": metrics.queue_depth,
        "messages_per_second": metrics.messages_per_second,
        "messages_per_minute": metrics.messages_per_minute,
        "messages_per_hour": metrics.messages_per_hour,
        "average_processing_time": metrics.average_processing_time,
        "oldest_message_age": metrics.oldest_message_age,
        "success_rate": metrics.success_rate,
        "error_rate": metrics.error_rate,
        "status": metrics.status,
        "timestamp": metrics.timestamp.isoformat()
    }


@router.get("/queues/{queue_name}/history")
async def get_queue_history(queue_name: str, limit: int = 100):
    """Get metrics history for a queue"""
    history = queue_monitor.get_metrics_history(queue_name, limit)
    return {
        "history": [
            {
                "queue_depth": m.queue_depth,
                "messages_per_second": m.messages_per_second,
                "status": m.status,
                "timestamp": m.timestamp.isoformat()
            }
            for m in history
        ],
        "count": len(history)
    }


@router.get("/queues/alerts/active")
async def get_active_alerts():
    """Get active backlog alerts"""
    alerts = queue_monitor.get_active_alerts()
    return {
        "alerts": [
            {
                "alert_id": a.alert_id,
                "queue_name": a.queue_name,
                "queue_depth": a.queue_depth,
                "severity": a.severity,
                "detected_at": a.detected_at.isoformat()
            }
            for a in alerts
        ],
        "count": len(alerts)
    }


@router.post("/queues/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve a backlog alert"""
    success = queue_monitor.resolve_alert(alert_id)
    if success:
        return {"message": "Alert resolved", "alert_id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/queues/statistics")
async def get_queue_statistics():
    """Get queue monitoring statistics"""
    return queue_monitor.get_statistics()


# Health Check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "remediation_engine": "operational",
            "retry_system": "operational",
            "service_manager": "operational",
            "queue_monitor": "operational"
        }
    }