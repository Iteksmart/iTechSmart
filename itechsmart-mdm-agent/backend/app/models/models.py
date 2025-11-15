"""
Database Models for iTechSmart MDM Deployment Agent

Defines SQLAlchemy models for deployments, configurations, health checks,
AI optimizations, and alerts.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class DeploymentStatus(str, enum.Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentStrategy(str, enum.Enum):
    """Deployment strategy enumeration"""
    DOCKER_COMPOSE = "docker_compose"
    KUBERNETES = "kubernetes"
    MANUAL = "manual"


class Environment(str, enum.Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class HealthStatus(str, enum.Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(str, enum.Enum):
    """Alert severity enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Deployment(Base):
    """Deployment model"""
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(String(100), unique=True, index=True, nullable=False)
    product_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=True)
    strategy = Column(SQLEnum(DeploymentStrategy), nullable=False)
    environment = Column(SQLEnum(Environment), nullable=False)
    status = Column(SQLEnum(DeploymentStatus), nullable=False, default=DeploymentStatus.PENDING)
    
    # Configuration
    configuration = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Deployment details
    port = Column(Integer, nullable=True)
    health_endpoint = Column(String(200), nullable=True)
    docker_image = Column(String(200), nullable=True)
    
    # Status details
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    
    # Relationships
    history_entries = relationship("DeploymentHistory", back_populates="deployment", cascade="all, delete-orphan")
    health_checks = relationship("HealthCheck", back_populates="deployment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Deployment(id={self.id}, product={self.product_name}, status={self.status})>"


class DeploymentHistory(Base):
    """Deployment history model"""
    __tablename__ = "deployment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # started, completed, failed, rolled_back, etc.
    message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    deployment = relationship("Deployment", back_populates="history_entries")
    
    def __repr__(self):
        return f"<DeploymentHistory(id={self.id}, event={self.event_type})>"


class Configuration(Base):
    """Configuration template model"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False, index=True)
    environment = Column(SQLEnum(Environment), nullable=False)
    
    # Configuration data
    template = Column(JSON, nullable=False)
    variables = Column(JSON, nullable=True)
    
    # Metadata
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Validation
    is_validated = Column(Boolean, default=False, nullable=False)
    validation_errors = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Configuration(id={self.id}, product={self.product_name}, env={self.environment})>"


class HealthCheck(Base):
    """Health check model"""
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=True)
    service_name = Column(String(100), nullable=False, index=True)
    
    # Health status
    status = Column(SQLEnum(HealthStatus), nullable=False)
    response_time = Column(Float, nullable=False)
    
    # Details
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    deployment = relationship("Deployment", back_populates="health_checks")
    
    def __repr__(self):
        return f"<HealthCheck(id={self.id}, service={self.service_name}, status={self.status})>"


class ServiceMetric(Base):
    """Service metrics model"""
    __tablename__ = "service_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    
    # Metrics
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    request_count = Column(Integer, nullable=False)
    error_count = Column(Integer, nullable=False)
    avg_response_time = Column(Float, nullable=False)
    
    # Additional metrics
    additional_metrics = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ServiceMetric(id={self.id}, service={self.service_name})>"


class AIOptimization(Base):
    """AI optimization recommendations model"""
    __tablename__ = "ai_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False, index=True)
    optimization_type = Column(String(50), nullable=False)  # resource, strategy, config, error_prediction, performance
    
    # Recommendations
    recommendations = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    
    # Context
    input_data = Column(JSON, nullable=True)
    environment = Column(SQLEnum(Environment), nullable=True)
    
    # Status
    applied = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime, nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AIOptimization(id={self.id}, product={self.product_name}, type={self.optimization_type})>"


class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, index=True, nullable=False)
    service_name = Column(String(100), nullable=False, index=True)
    
    # Alert details
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Status
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Auto-healing
    auto_heal_triggered = Column(Boolean, default=False, nullable=False)
    auto_heal_successful = Column(Boolean, nullable=True)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, service={self.service_name}, severity={self.severity})>"


class DeploymentPlan(Base):
    """Deployment plan model"""
    __tablename__ = "deployment_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Plan details
    products = Column(JSON, nullable=False)  # List of products to deploy
    strategy = Column(SQLEnum(DeploymentStrategy), nullable=False)
    environment = Column(SQLEnum(Environment), nullable=False)
    
    # Execution order
    execution_order = Column(JSON, nullable=False)  # Ordered list based on dependencies
    
    # AI recommendations
    ai_optimized = Column(Boolean, default=False, nullable=False)
    ai_recommendations = Column(JSON, nullable=True)
    
    # Status
    executed = Column(Boolean, default=False, nullable=False)
    execution_status = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DeploymentPlan(id={self.id}, name={self.name})>"


class SystemSetting(Base):
    """System settings model"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    category = Column(String(50), nullable=True)
    is_sensitive = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SystemSetting(key={self.key})>"