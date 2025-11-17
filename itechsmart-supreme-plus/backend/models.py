"""
iTechSmart Supreme Plus - Database Models
AI-Powered Infrastructure Auto-Remediation Platform
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class IncidentStatus(enum.Enum):
    """Incident status enumeration"""

    DETECTED = "detected"
    ANALYZING = "analyzing"
    DIAGNOSED = "diagnosed"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class RemediationMode(enum.Enum):
    """Remediation mode enumeration"""

    MANUAL = "manual"
    SEMI_AUTOMATIC = "semi_automatic"
    FULLY_AUTOMATIC = "fully_automatic"


class SeverityLevel(enum.Enum):
    """Severity level enumeration"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CommandProtocol(enum.Enum):
    """Command execution protocol"""

    SSH = "ssh"
    WINRM = "winrm"
    POWERSHELL = "powershell"
    TELNET = "telnet"
    NETMIKO = "netmiko"
    CLI = "cli"
    API = "api"


class Server(Base):
    """Server/Infrastructure Node Model"""

    __tablename__ = "servers"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    os_type = Column(String(50))  # linux, windows, network_device
    os_version = Column(String(100))

    # Connection details
    ssh_port = Column(Integer, default=22)
    winrm_port = Column(Integer, default=5985)
    protocol = Column(Enum(CommandProtocol), default=CommandProtocol.SSH)

    # Credentials (encrypted)
    credential_id = Column(String(36), ForeignKey("credentials.id"))

    # Monitoring
    prometheus_endpoint = Column(String(500))
    wazuh_agent_id = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime)
    health_status = Column(String(50))  # healthy, degraded, critical, offline

    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credential = relationship("Credential", back_populates="servers")
    incidents = relationship("Incident", back_populates="server")
    metrics = relationship("ServerMetric", back_populates="server")
    commands = relationship("CommandExecution", back_populates="server")


class Credential(Base):
    """Secure credential storage"""

    __tablename__ = "credentials"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    credential_type = Column(String(50))  # ssh_key, password, api_token

    # Encrypted credentials
    username = Column(String(255))
    encrypted_password = Column(Text)
    encrypted_private_key = Column(Text)
    encrypted_api_token = Column(Text)

    # Vault reference
    vault_path = Column(String(500))

    # Metadata
    description = Column(Text)
    tags = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    servers = relationship("Server", back_populates="credential")


class Incident(Base):
    """Infrastructure incident/issue"""

    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Classification
    incident_type = Column(
        String(100)
    )  # high_cpu, disk_full, service_down, security_breach, etc.
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MEDIUM)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.DETECTED)

    # Source
    source = Column(String(100))  # prometheus, wazuh, manual, api
    alert_id = Column(String(255))

    # Server reference
    server_id = Column(String(36), ForeignKey("servers.id"))

    # AI Analysis
    ai_diagnosis = Column(Text)
    root_cause = Column(Text)
    confidence_score = Column(Float)  # 0.0 to 1.0

    # Remediation
    remediation_mode = Column(
        Enum(RemediationMode), default=RemediationMode.SEMI_AUTOMATIC
    )
    proposed_fix = Column(Text)
    fix_command = Column(Text)
    fix_protocol = Column(Enum(CommandProtocol))

    # Approval workflow
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)

    # Execution
    executed_at = Column(DateTime)
    execution_output = Column(Text)
    execution_error = Column(Text)

    # Resolution
    resolved_at = Column(DateTime)
    resolution_time_seconds = Column(Integer)
    was_auto_resolved = Column(Boolean, default=False)

    # Impact
    affected_services = Column(JSON)
    business_impact = Column(String(50))  # none, low, medium, high, critical

    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    server = relationship("Server", back_populates="incidents")
    logs = relationship("IncidentLog", back_populates="incident")
    commands = relationship("CommandExecution", back_populates="incident")


class IncidentLog(Base):
    """Audit log for incident lifecycle"""

    __tablename__ = "incident_logs"

    id = Column(String(36), primary_key=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)

    # Log entry
    action = Column(
        String(100), nullable=False
    )  # detected, analyzed, approved, executed, resolved
    description = Column(Text)

    # Actor
    actor_type = Column(String(50))  # ai, user, system
    actor_id = Column(String(255))

    # Data
    previous_state = Column(JSON)
    new_state = Column(JSON)
    metadata = Column(JSON)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    incident = relationship("Incident", back_populates="logs")


class CommandExecution(Base):
    """Command execution history"""

    __tablename__ = "command_executions"

    id = Column(String(36), primary_key=True)

    # References
    incident_id = Column(String(36), ForeignKey("incidents.id"))
    server_id = Column(String(36), ForeignKey("servers.id"), nullable=False)

    # Command details
    command = Column(Text, nullable=False)
    protocol = Column(Enum(CommandProtocol), nullable=False)

    # Execution
    executed_by = Column(String(255))  # user or 'ai'
    executed_at = Column(DateTime, default=datetime.utcnow)

    # Results
    exit_code = Column(Integer)
    stdout = Column(Text)
    stderr = Column(Text)
    execution_time_ms = Column(Integer)

    # Status
    status = Column(String(50))  # pending, running, completed, failed, timeout
    error_message = Column(Text)

    # Safety
    was_sandboxed = Column(Boolean, default=True)
    was_approved = Column(Boolean, default=False)
    risk_level = Column(String(50))  # low, medium, high, critical

    # Metadata
    metadata = Column(JSON)

    # Relationships
    incident = relationship("Incident", back_populates="commands")
    server = relationship("Server", back_populates="commands")


class ServerMetric(Base):
    """Server performance metrics"""

    __tablename__ = "server_metrics"

    id = Column(String(36), primary_key=True)
    server_id = Column(String(36), ForeignKey("servers.id"), nullable=False)

    # Metrics
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    memory_used_mb = Column(Float)
    memory_total_mb = Column(Float)
    disk_percent = Column(Float)
    disk_used_gb = Column(Float)
    disk_total_gb = Column(Float)

    # Network
    network_rx_mbps = Column(Float)
    network_tx_mbps = Column(Float)

    # Load
    load_1min = Column(Float)
    load_5min = Column(Float)
    load_15min = Column(Float)

    # Processes
    process_count = Column(Integer)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    server = relationship("Server", back_populates="metrics")


class AutomationRule(Base):
    """Automation rules for auto-remediation"""

    __tablename__ = "automation_rules"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Trigger conditions
    incident_type = Column(String(100))
    severity_threshold = Column(Enum(SeverityLevel))

    # Conditions (JSON query)
    conditions = Column(JSON)  # Complex matching rules

    # Action
    remediation_mode = Column(
        Enum(RemediationMode), default=RemediationMode.SEMI_AUTOMATIC
    )
    command_template = Column(Text)
    protocol = Column(Enum(CommandProtocol))

    # Safety
    requires_approval = Column(Boolean, default=True)
    max_executions_per_hour = Column(Integer, default=10)

    # Status
    is_active = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)

    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed_at = Column(DateTime)


class KnowledgeBase(Base):
    """Knowledge base for AI learning"""

    __tablename__ = "knowledge_base"

    id = Column(String(36), primary_key=True)
    title = Column(String(500), nullable=False)

    # Content
    problem_description = Column(Text)
    solution_description = Column(Text)
    command = Column(Text)
    protocol = Column(Enum(CommandProtocol))

    # Classification
    incident_type = Column(String(100))
    severity = Column(Enum(SeverityLevel))
    os_type = Column(String(50))

    # Effectiveness
    success_rate = Column(Float)  # 0.0 to 1.0
    usage_count = Column(Integer, default=0)

    # Source
    source = Column(String(100))  # manual, ai_learned, imported
    verified = Column(Boolean, default=False)
    verified_by = Column(String(255))

    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Integration(Base):
    """External system integrations"""

    __tablename__ = "integrations"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    integration_type = Column(
        String(100)
    )  # prometheus, wazuh, jira, servicenow, slack, etc.

    # Configuration
    endpoint_url = Column(String(500))
    api_key_encrypted = Column(Text)
    webhook_url = Column(String(500))

    # Settings
    config = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    health_status = Column(String(50))

    # Metadata
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """Incoming alerts from monitoring systems"""

    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True)

    # Source
    source = Column(String(100), nullable=False)  # prometheus, wazuh, custom
    alert_name = Column(String(255), nullable=False)

    # Details
    severity = Column(Enum(SeverityLevel))
    description = Column(Text)

    # Target
    server_id = Column(String(36), ForeignKey("servers.id"))

    # Status
    status = Column(String(50))  # firing, resolved, acknowledged

    # Processing
    processed = Column(Boolean, default=False)
    incident_id = Column(String(36), ForeignKey("incidents.id"))

    # Raw data
    raw_payload = Column(JSON)

    # Timestamps
    alert_timestamp = Column(DateTime)
    received_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)


class AuditLog(Base):
    """Comprehensive audit logging"""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)

    # Event
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50))  # access, change, execution, approval

    # Actor
    user_id = Column(String(255))
    user_email = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Target
    resource_type = Column(String(100))
    resource_id = Column(String(255))

    # Action
    action = Column(String(100))
    description = Column(Text)

    # Data
    before_state = Column(JSON)
    after_state = Column(JSON)

    # Result
    success = Column(Boolean)
    error_message = Column(Text)

    # Metadata
    metadata = Column(JSON)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)


class Dashboard(Base):
    """Custom dashboards"""

    __tablename__ = "dashboards"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Configuration
    layout = Column(JSON)  # Widget layout and configuration

    # Access
    is_public = Column(Boolean, default=False)
    owner_id = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """Notification queue"""

    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True)

    # Type
    notification_type = Column(String(100))  # email, slack, teams, sms, webhook

    # Target
    recipient = Column(String(500))

    # Content
    subject = Column(String(500))
    message = Column(Text)

    # Context
    incident_id = Column(String(36), ForeignKey("incidents.id"))
    severity = Column(Enum(SeverityLevel))

    # Status
    status = Column(String(50))  # pending, sent, failed
    sent_at = Column(DateTime)
    error_message = Column(Text)

    # Metadata
    metadata = Column(JSON)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
