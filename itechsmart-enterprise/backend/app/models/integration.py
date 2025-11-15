"""
Database models for integration hub
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float
from datetime import datetime

from app.core.database import Base


class RegisteredService(Base):
    """Registry of all iTechSmart services"""
    __tablename__ = "registered_services"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(String(200), unique=True, index=True)
    service_type = Column(String(100), index=True)
    service_name = Column(String(200))
    base_url = Column(String(500))
    api_key = Column(String(500))
    capabilities = Column(JSON)  # List of capabilities
    metadata = Column(JSON)  # Additional metadata
    status = Column(String(50), default="active")  # active, inactive, error
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)


class ServiceHealth(Base):
    """Health check results for services"""
    __tablename__ = "service_health"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(String(200), index=True)
    status = Column(String(50))  # healthy, degraded, unhealthy
    response_time_ms = Column(Float)
    metrics = Column(JSON)  # CPU, memory, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class IntegrationEvent(Base):
    """Events broadcast across services"""
    __tablename__ = "integration_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), index=True)
    event_data = Column(JSON)
    source_service = Column(String(200), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    processed = Column(Boolean, default=False)


class CrossServiceCall(Base):
    """Log of cross-service API calls"""
    __tablename__ = "cross_service_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    source_service = Column(String(200), index=True)
    target_service = Column(String(200), index=True)
    endpoint = Column(String(500))
    method = Column(String(10))
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ServiceDependency(Base):
    """Service dependency mapping"""
    __tablename__ = "service_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(String(200), index=True)
    depends_on_service = Column(String(200), index=True)
    dependency_type = Column(String(50))  # required, optional
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkflowExecution(Base):
    """Cross-service workflow executions"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(200), index=True)
    steps = Column(JSON)  # List of workflow steps
    results = Column(JSON)  # Results from each step
    status = Column(String(50))  # running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class NinjaControlLog(Base):
    """Log of Ninja control commands"""
    __tablename__ = "ninja_control_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    target_service = Column(String(200), index=True)
    command = Column(String(100))  # fix, update, restart, optimize
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    success = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)