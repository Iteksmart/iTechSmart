"""
Core data models for iTechSmart Supreme
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class SeverityLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(Enum):
    """Remediation action status"""
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"


class Platform(Enum):
    """Target platform types"""
    LINUX = "linux"
    WINDOWS = "windows"
    NETWORK = "network"
    CONTAINER = "container"
    CLOUD = "cloud"


class AlertSource(Enum):
    """Alert source systems"""
    PROMETHEUS = "prometheus"
    WAZUH = "wazuh"
    GITHUB = "github"
    CUSTOM = "custom"
    SYSTEM = "system"


@dataclass
class Alert:
    """Alert data model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: AlertSource = AlertSource.SYSTEM
    severity: SeverityLevel = SeverityLevel.MEDIUM
    message: str = ""
    host: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class Diagnosis:
    """AI diagnosis result"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    root_cause: str = ""
    confidence: float = 0.0  # 0-100
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    ai_model: str = "offline"


@dataclass
class RemediationAction:
    """Remediation action to be executed"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    diagnosis_id: str = ""
    command: str = ""
    platform: Platform = Platform.LINUX
    risk_level: SeverityLevel = SeverityLevel.MEDIUM
    description: str = ""
    estimated_impact: str = ""
    requires_approval: bool = True
    status: ActionStatus = ActionStatus.PENDING
    rollback_command: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    execution_result: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None


@dataclass
class ExecutionResult:
    """Command execution result"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_id: str = ""
    success: bool = False
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class HostCredentials:
    """Host connection credentials"""
    host: str
    username: str
    password: Optional[str] = None
    private_key: Optional[str] = None
    port: int = 22
    platform: Platform = Platform.LINUX
    domain: Optional[str] = None  # For Windows domain credentials
    use_sudo: bool = False


@dataclass
class SystemHealth:
    """System health metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    network_connections: int = 0
    active_processes: int = 0
    uptime_seconds: int = 0
    load_average: List[float] = field(default_factory=list)


@dataclass
class AuditLog:
    """Audit log entry"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    action_type: str = ""
    user: str = "system"
    target: str = ""
    command: str = ""
    result: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalWorkflow:
    """Approval workflow configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_id: str = ""
    required_approvers: List[str] = field(default_factory=list)
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"
    timeout_minutes: int = 60
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None