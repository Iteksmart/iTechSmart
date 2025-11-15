"""
iTechSmart Sentinel - Database Models
Observability & Incident Management Platform
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SeverityLevel(str, Enum):
    """Severity levels for alerts and incidents"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentStatus(str, Enum):
    """Incident lifecycle status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertStatus(str, Enum):
    """Alert status"""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


class SLOStatus(str, Enum):
    """SLO compliance status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    BREACHED = "breached"


class Service(Base):
    """Service being monitored"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    description = Column(Text)
    version = Column(String(50))
    environment = Column(String(50), default="production")  # dev, staging, production
    
    # Service metadata
    team = Column(String(100))
    owner = Column(String(100))
    repository_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Health status
    is_healthy = Column(Boolean, default=True)
    last_health_check = Column(DateTime)
    uptime_percentage = Column(Float, default=100.0)
    
    # Relationships
    traces = relationship("Trace", back_populates="service", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="service", cascade="all, delete-orphan")
    logs = relationship("LogEntry", back_populates="service", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="service", cascade="all, delete-orphan")
    slos = relationship("SLO", back_populates="service", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_service_name_env', 'name', 'environment'),
    )


class Trace(Base):
    """Distributed trace for request tracking"""
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(100), unique=True, nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    # Trace metadata
    operation_name = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    duration_ms = Column(Float)  # Duration in milliseconds
    
    # Status
    status_code = Column(Integer)  # HTTP status or custom code
    is_error = Column(Boolean, default=False, index=True)
    error_message = Column(Text)
    
    # Request details
    http_method = Column(String(10))
    http_url = Column(String(1000))
    user_agent = Column(String(500))
    client_ip = Column(String(50))
    
    # Tags and metadata
    tags = Column(JSON)  # Custom tags
    metadata = Column(JSON)  # Additional metadata
    
    # Relationships
    service = relationship("Service", back_populates="traces")
    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_trace_service_time', 'service_id', 'start_time'),
        Index('idx_trace_error', 'is_error', 'start_time'),
    )


class Span(Base):
    """Individual span within a trace"""
    __tablename__ = "spans"

    id = Column(Integer, primary_key=True, index=True)
    span_id = Column(String(100), unique=True, nullable=False, index=True)
    trace_id = Column(Integer, ForeignKey("traces.id"), nullable=False)
    parent_span_id = Column(String(100))  # For nested spans
    
    # Span details
    operation_name = Column(String(200), nullable=False)
    service_name = Column(String(200))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_ms = Column(Float)
    
    # Status
    is_error = Column(Boolean, default=False)
    error_message = Column(Text)
    
    # Span type
    span_type = Column(String(50))  # http, db, cache, external, etc.
    
    # Tags and metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Relationships
    trace = relationship("Trace", back_populates="spans")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_span_trace', 'trace_id', 'start_time'),
    )


class Metric(Base):
    """Time-series metrics"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    # Metric identification
    metric_name = Column(String(200), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram, summary
    
    # Metric value
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Labels/Tags
    labels = Column(JSON)  # Key-value pairs for filtering
    
    # Unit
    unit = Column(String(50))  # ms, bytes, requests, etc.
    
    # Relationships
    service = relationship("Service", back_populates="metrics")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_metric_service_name_time', 'service_id', 'metric_name', 'timestamp'),
    )


class LogEntry(Base):
    """Centralized log entries"""
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    # Log details
    timestamp = Column(DateTime, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    
    # Context
    logger_name = Column(String(200))
    file_name = Column(String(500))
    line_number = Column(Integer)
    function_name = Column(String(200))
    
    # Trace correlation
    trace_id = Column(String(100), index=True)
    span_id = Column(String(100))
    
    # Additional data
    tags = Column(JSON)
    metadata = Column(JSON)
    stack_trace = Column(Text)
    
    # Anomaly detection
    is_anomaly = Column(Boolean, default=False, index=True)
    anomaly_score = Column(Float)
    
    # Relationships
    service = relationship("Service", back_populates="logs")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_log_service_level_time', 'service_id', 'level', 'timestamp'),
        Index('idx_log_trace', 'trace_id', 'timestamp'),
    )


class Alert(Base):
    """Alert definitions and instances"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    # Alert identification
    alert_name = Column(String(200), nullable=False)
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, pattern, slo_breach
    
    # Alert details
    severity = Column(String(20), nullable=False, index=True)  # SeverityLevel enum
    status = Column(String(20), nullable=False, default="firing", index=True)  # AlertStatus enum
    
    # Trigger information
    triggered_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    
    # Alert content
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Condition that triggered
    condition = Column(JSON)  # The condition that was met
    current_value = Column(Float)
    threshold_value = Column(Float)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON)  # List of channels notified
    
    # Grouping and deduplication
    fingerprint = Column(String(100), index=True)  # For deduplication
    group_key = Column(String(100))  # For grouping related alerts
    
    # Incident correlation
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Relationships
    service = relationship("Service", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_alert_service_status', 'service_id', 'status', 'triggered_at'),
        Index('idx_alert_severity', 'severity', 'triggered_at'),
    )


class Incident(Base):
    """Incident tracking and management"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    
    # Incident identification
    incident_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Status and severity
    status = Column(String(20), nullable=False, default="open", index=True)  # IncidentStatus enum
    severity = Column(String(20), nullable=False, index=True)  # SeverityLevel enum
    
    # Timeline
    detected_at = Column(DateTime, nullable=False, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Assignment
    assigned_to = Column(String(100))
    team = Column(String(100))
    
    # Impact
    affected_services = Column(JSON)  # List of affected service IDs
    affected_users = Column(Integer)
    estimated_impact = Column(Text)
    
    # Root cause
    root_cause = Column(Text)
    resolution_summary = Column(Text)
    
    # Post-mortem
    post_mortem_url = Column(String(500))
    lessons_learned = Column(Text)
    action_items = Column(JSON)
    
    # Communication
    war_room_url = Column(String(500))
    status_page_updated = Column(Boolean, default=False)
    
    # Metrics
    time_to_detect_minutes = Column(Float)
    time_to_acknowledge_minutes = Column(Float)
    time_to_resolve_minutes = Column(Float)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Relationships
    alerts = relationship("Alert", back_populates="incident")
    updates = relationship("IncidentUpdate", back_populates="incident", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_incident_status_severity', 'status', 'severity', 'detected_at'),
    )


class IncidentUpdate(Base):
    """Timeline updates for incidents"""
    __tablename__ = "incident_updates"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Update details
    update_type = Column(String(50), nullable=False)  # status_change, investigation, resolution, etc.
    message = Column(Text, nullable=False)
    
    # Author
    author = Column(String(100), nullable=False)
    
    # Metadata
    metadata = Column(JSON)
    
    # Relationships
    incident = relationship("Incident", back_populates="updates")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SLO(Base):
    """Service Level Objective definitions and tracking"""
    __tablename__ = "slos"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    # SLO identification
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # SLO definition
    slo_type = Column(String(50), nullable=False)  # availability, latency, error_rate, custom
    target_percentage = Column(Float, nullable=False)  # e.g., 99.9
    
    # Time window
    window_days = Column(Integer, nullable=False, default=30)  # Rolling window in days
    
    # Current status
    current_percentage = Column(Float)
    status = Column(String(20), default="healthy")  # SLOStatus enum
    
    # Error budget
    error_budget_remaining = Column(Float)  # Percentage remaining
    error_budget_consumed = Column(Float)  # Percentage consumed
    burn_rate = Column(Float)  # Current burn rate
    
    # Thresholds
    warning_threshold = Column(Float, default=95.0)  # Warn at 95% of target
    critical_threshold = Column(Float, default=90.0)  # Critical at 90% of target
    
    # Alerting
    alert_on_breach = Column(Boolean, default=True)
    alert_on_burn_rate = Column(Boolean, default=True)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Relationships
    service = relationship("Service", back_populates="slos")
    measurements = relationship("SLOMeasurement", back_populates="slo", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_slo_service_status', 'service_id', 'status'),
    )


class SLOMeasurement(Base):
    """Time-series measurements for SLO tracking"""
    __tablename__ = "slo_measurements"

    id = Column(Integer, primary_key=True, index=True)
    slo_id = Column(Integer, ForeignKey("slos.id"), nullable=False)
    
    # Measurement
    timestamp = Column(DateTime, nullable=False, index=True)
    success_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    success_percentage = Column(Float)
    
    # Error budget
    error_budget_consumed = Column(Float)
    burn_rate = Column(Float)
    
    # Relationships
    slo = relationship("SLO", back_populates="measurements")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_slo_measurement_time', 'slo_id', 'timestamp'),
    )


class OnCallSchedule(Base):
    """On-call rotation schedule"""
    __tablename__ = "oncall_schedules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Schedule details
    name = Column(String(200), nullable=False)
    team = Column(String(100))
    
    # Current on-call
    current_oncall = Column(String(100))
    current_shift_start = Column(DateTime)
    current_shift_end = Column(DateTime)
    
    # Rotation
    rotation_type = Column(String(50), default="weekly")  # daily, weekly, custom
    rotation_members = Column(JSON)  # List of team members
    
    # Escalation
    escalation_policy = Column(JSON)  # Escalation rules
    
    # Notification preferences
    notification_channels = Column(JSON)
    
    # Metadata
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Runbook(Base):
    """Automated runbooks for incident response"""
    __tablename__ = "runbooks"

    id = Column(Integer, primary_key=True, index=True)
    
    # Runbook identification
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    
    # Trigger conditions
    trigger_type = Column(String(50), nullable=False)  # alert, incident, manual
    trigger_conditions = Column(JSON)
    
    # Steps
    steps = Column(JSON, nullable=False)  # List of automated steps
    
    # Execution
    is_automated = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    
    # Statistics
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    average_duration_seconds = Column(Float)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RunbookExecution(Base):
    """Runbook execution history"""
    __tablename__ = "runbook_executions"

    id = Column(Integer, primary_key=True, index=True)
    runbook_id = Column(Integer, ForeignKey("runbooks.id"), nullable=False)
    
    # Execution details
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Status
    status = Column(String(50), nullable=False)  # running, success, failed, cancelled
    
    # Trigger
    triggered_by = Column(String(100))
    trigger_reason = Column(Text)
    
    # Results
    steps_completed = Column(Integer, default=0)
    steps_failed = Column(Integer, default=0)
    execution_log = Column(JSON)  # Detailed log of each step
    
    # Output
    output = Column(JSON)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)