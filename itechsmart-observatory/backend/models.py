"""
iTechSmart Observatory - Database Models
Product #36: Application Performance Monitoring & Observability Platform

This module defines the database models for the Observatory system including:
- Metrics and time-series data
- Distributed traces and spans
- Log entries and aggregation
- Alerts and notifications
- Dashboards and visualizations
- Service topology and dependencies
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Service(Base):
    """
    Represents a monitored service or application
    """
    __tablename__ = "observatory_services"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    service_type = Column(String(50), nullable=False)  # web, api, database, queue, cache, etc.
    environment = Column(String(50), nullable=False, index=True)  # production, staging, development
    version = Column(String(50))
    language = Column(String(50))  # python, java, nodejs, go, etc.
    framework = Column(String(100))  # django, spring, express, gin, etc.
    
    # Service metadata
    metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])
    
    # Health status
    health_status = Column(String(20), default="unknown")  # healthy, degraded, unhealthy, unknown
    last_seen = Column(DateTime)
    
    # Configuration
    sampling_rate = Column(Float, default=1.0)  # 0.0 to 1.0
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metrics = relationship("Metric", back_populates="service", cascade="all, delete-orphan")
    traces = relationship("Trace", back_populates="service", cascade="all, delete-orphan")
    logs = relationship("LogEntry", back_populates="service", cascade="all, delete-orphan")
    dependencies = relationship("ServiceDependency", foreign_keys="ServiceDependency.service_id", back_populates="service")

    __table_args__ = (
        Index('idx_service_env_type', 'environment', 'service_type'),
        Index('idx_service_health', 'health_status', 'is_active'),
    )


class Metric(Base):
    """
    Time-series metrics data
    """
    __tablename__ = "observatory_metrics"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # Metric identification
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(20), nullable=False)  # counter, gauge, histogram, summary
    
    # Metric value
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # ms, bytes, requests, percent, etc.
    
    # Dimensions/Labels
    labels = Column(JSON, default={})  # {host: "server1", endpoint: "/api/users"}
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Aggregation metadata
    aggregation_type = Column(String(20))  # sum, avg, min, max, p50, p95, p99
    sample_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="metrics")

    __table_args__ = (
        Index('idx_metric_service_name_time', 'service_id', 'metric_name', 'timestamp'),
        Index('idx_metric_name_time', 'metric_name', 'timestamp'),
    )


class Trace(Base):
    """
    Distributed trace representing a request flow
    """
    __tablename__ = "observatory_traces"

    id = Column(String(36), primary_key=True)  # trace_id
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # Trace metadata
    trace_name = Column(String(255), nullable=False)
    operation = Column(String(255))
    
    # Timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    duration_ms = Column(Float)
    
    # Status
    status = Column(String(20), default="ok")  # ok, error, timeout
    error_message = Column(Text)
    
    # Request context
    http_method = Column(String(10))
    http_url = Column(Text)
    http_status_code = Column(Integer)
    
    # Trace attributes
    attributes = Column(JSON, default={})
    tags = Column(JSON, default=[])
    
    # Sampling
    is_sampled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="traces")
    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_trace_service_time', 'service_id', 'start_time'),
        Index('idx_trace_status', 'status', 'start_time'),
    )


class Span(Base):
    """
    Individual span within a distributed trace
    """
    __tablename__ = "observatory_spans"

    id = Column(String(36), primary_key=True)  # span_id
    trace_id = Column(String(36), ForeignKey("observatory_traces.id"), nullable=False, index=True)
    parent_span_id = Column(String(36), index=True)
    
    # Span metadata
    span_name = Column(String(255), nullable=False)
    span_kind = Column(String(20))  # server, client, producer, consumer, internal
    
    # Service info
    service_name = Column(String(255), nullable=False, index=True)
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_ms = Column(Float)
    
    # Status
    status = Column(String(20), default="ok")
    error_message = Column(Text)
    
    # Span attributes
    attributes = Column(JSON, default={})
    events = Column(JSON, default=[])  # [{timestamp, name, attributes}]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trace = relationship("Trace", back_populates="spans")

    __table_args__ = (
        Index('idx_span_trace_parent', 'trace_id', 'parent_span_id'),
        Index('idx_span_service_time', 'service_name', 'start_time'),
    )


class LogEntry(Base):
    """
    Application log entries
    """
    __tablename__ = "observatory_logs"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # Log metadata
    timestamp = Column(DateTime, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Log content
    message = Column(Text, nullable=False)
    logger_name = Column(String(255))
    
    # Context
    trace_id = Column(String(36), index=True)
    span_id = Column(String(36))
    
    # Source
    host = Column(String(255))
    process_id = Column(String(50))
    thread_id = Column(String(50))
    
    # Structured data
    attributes = Column(JSON, default={})
    stack_trace = Column(Text)
    
    # Categorization
    tags = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="logs")

    __table_args__ = (
        Index('idx_log_service_time_level', 'service_id', 'timestamp', 'level'),
        Index('idx_log_trace', 'trace_id', 'timestamp'),
    )


class Alert(Base):
    """
    Alert definitions and rules
    """
    __tablename__ = "observatory_alerts"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Alert configuration
    alert_type = Column(String(50), nullable=False)  # metric_threshold, anomaly, error_rate, latency, etc.
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    
    # Target
    service_id = Column(String(36), ForeignKey("observatory_services.id"), index=True)
    metric_name = Column(String(255))
    
    # Conditions
    condition = Column(JSON, nullable=False)  # {operator: "gt", threshold: 100, duration: 300}
    evaluation_window = Column(Integer, default=300)  # seconds
    
    # Notification
    notification_channels = Column(JSON, default=[])  # [email, slack, pagerduty, webhook]
    notification_config = Column(JSON, default={})
    
    # State
    is_active = Column(Boolean, default=True)
    is_firing = Column(Boolean, default=False)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    
    # Suppression
    silence_until = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36))
    
    # Relationships
    incidents = relationship("AlertIncident", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_alert_service_active', 'service_id', 'is_active'),
        Index('idx_alert_firing', 'is_firing', 'severity'),
    )


class AlertIncident(Base):
    """
    Alert incident occurrences
    """
    __tablename__ = "observatory_alert_incidents"

    id = Column(String(36), primary_key=True)
    alert_id = Column(String(36), ForeignKey("observatory_alerts.id"), nullable=False, index=True)
    
    # Incident details
    status = Column(String(20), nullable=False, default="firing")  # firing, acknowledged, resolved
    severity = Column(String(20), nullable=False)
    
    # Timing
    started_at = Column(DateTime, nullable=False, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Context
    trigger_value = Column(Float)
    trigger_context = Column(JSON, default={})
    
    # Response
    acknowledged_by = Column(String(36))
    resolved_by = Column(String(36))
    resolution_notes = Column(Text)
    
    # Notifications
    notifications_sent = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alert = relationship("Alert", back_populates="incidents")

    __table_args__ = (
        Index('idx_incident_alert_status', 'alert_id', 'status'),
        Index('idx_incident_time', 'started_at', 'status'),
    )


class Dashboard(Base):
    """
    Custom monitoring dashboards
    """
    __tablename__ = "observatory_dashboards"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Dashboard configuration
    layout = Column(JSON, nullable=False)  # Grid layout configuration
    widgets = Column(JSON, nullable=False)  # Widget definitions
    
    # Filters
    default_time_range = Column(String(50), default="1h")  # 5m, 15m, 1h, 6h, 24h, 7d, 30d
    default_filters = Column(JSON, default={})
    
    # Access control
    is_public = Column(Boolean, default=False)
    owner_id = Column(String(36), nullable=False)
    shared_with = Column(JSON, default=[])  # List of user/team IDs
    
    # Metadata
    tags = Column(JSON, default=[])
    is_favorite = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_dashboard_owner', 'owner_id', 'is_public'),
    )


class ServiceDependency(Base):
    """
    Service-to-service dependencies
    """
    __tablename__ = "observatory_service_dependencies"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    depends_on_service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # Dependency metadata
    dependency_type = Column(String(50), nullable=False)  # http, grpc, database, queue, cache
    protocol = Column(String(50))
    
    # Traffic metrics
    request_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    avg_latency_ms = Column(Float)
    
    # Health
    health_status = Column(String(20), default="unknown")
    last_checked = Column(DateTime)
    
    # Discovery
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", foreign_keys=[service_id], back_populates="dependencies")

    __table_args__ = (
        Index('idx_dependency_services', 'service_id', 'depends_on_service_id'),
    )


class MetricAggregation(Base):
    """
    Pre-aggregated metrics for faster queries
    """
    __tablename__ = "observatory_metric_aggregations"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    
    # Time bucket
    time_bucket = Column(DateTime, nullable=False, index=True)
    bucket_size = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d
    
    # Aggregated values
    count = Column(Integer, default=0)
    sum = Column(Float, default=0.0)
    min = Column(Float)
    max = Column(Float)
    avg = Column(Float)
    p50 = Column(Float)
    p95 = Column(Float)
    p99 = Column(Float)
    
    # Labels
    labels = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_agg_service_metric_time', 'service_id', 'metric_name', 'time_bucket'),
        Index('idx_agg_bucket', 'bucket_size', 'time_bucket'),
    )


class AnomalyDetection(Base):
    """
    Detected anomalies in metrics and traces
    """
    __tablename__ = "observatory_anomalies"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # Anomaly details
    anomaly_type = Column(String(50), nullable=False)  # spike, drop, trend_change, outlier
    metric_name = Column(String(255))
    
    # Detection
    detected_at = Column(DateTime, nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    # Values
    expected_value = Column(Float)
    actual_value = Column(Float)
    deviation_percent = Column(Float)
    
    # Context
    context = Column(JSON, default={})
    
    # Status
    status = Column(String(20), default="open")  # open, investigating, resolved, false_positive
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_anomaly_service_time', 'service_id', 'detected_at'),
        Index('idx_anomaly_status', 'status', 'severity'),
    )


class SLO(Base):
    """
    Service Level Objectives
    """
    __tablename__ = "observatory_slos"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # SLO definition
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slo_type = Column(String(50), nullable=False)  # availability, latency, error_rate, throughput
    
    # Target
    target_value = Column(Float, nullable=False)  # e.g., 99.9 for availability
    target_unit = Column(String(20))  # percent, ms, requests_per_second
    
    # Measurement
    metric_name = Column(String(255), nullable=False)
    measurement_window = Column(String(20), default="30d")  # 1d, 7d, 30d, 90d
    
    # Current status
    current_value = Column(Float)
    compliance_status = Column(String(20), default="unknown")  # compliant, at_risk, breached, unknown
    error_budget_remaining = Column(Float)  # Percentage of error budget left
    
    # Thresholds
    warning_threshold = Column(Float)  # Alert when approaching breach
    
    # Metadata
    is_active = Column(Boolean, default=True)
    last_evaluated = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_slo_service_active', 'service_id', 'is_active'),
        Index('idx_slo_compliance', 'compliance_status', 'is_active'),
    )


class Annotation(Base):
    """
    Timeline annotations for deployments, incidents, etc.
    """
    __tablename__ = "observatory_annotations"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), index=True)
    
    # Annotation details
    annotation_type = Column(String(50), nullable=False)  # deployment, incident, maintenance, release
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Timing
    timestamp = Column(DateTime, nullable=False, index=True)
    end_timestamp = Column(DateTime)  # For events with duration
    
    # Metadata
    tags = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    
    # Source
    source = Column(String(100))  # manual, ci_cd, incident_management
    created_by = Column(String(36))
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_annotation_service_time', 'service_id', 'timestamp'),
        Index('idx_annotation_type', 'annotation_type', 'timestamp'),
    )


class SyntheticCheck(Base):
    """
    Synthetic monitoring checks
    """
    __tablename__ = "observatory_synthetic_checks"

    id = Column(String(36), primary_key=True)
    service_id = Column(String(36), ForeignKey("observatory_services.id"), nullable=False, index=True)
    
    # Check configuration
    name = Column(String(255), nullable=False)
    check_type = Column(String(50), nullable=False)  # http, tcp, dns, ssl, api
    
    # Target
    target_url = Column(String(500))
    target_host = Column(String(255))
    target_port = Column(Integer)
    
    # Check settings
    interval_seconds = Column(Integer, default=60)
    timeout_seconds = Column(Integer, default=30)
    
    # Validation
    expected_status_code = Column(Integer)
    expected_response_time_ms = Column(Integer)
    expected_content = Column(Text)
    
    # Locations
    check_locations = Column(JSON, default=[])  # List of geographic locations
    
    # Status
    is_active = Column(Boolean, default=True)
    last_check_time = Column(DateTime)
    last_check_status = Column(String(20))  # success, failure, timeout
    last_check_duration_ms = Column(Float)
    
    # Statistics
    success_rate = Column(Float)
    avg_response_time_ms = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_synthetic_service_active', 'service_id', 'is_active'),
    )