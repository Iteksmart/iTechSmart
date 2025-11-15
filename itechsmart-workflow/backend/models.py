"""
iTechSmart Workflow - Database Models
Business Process Automation Platform
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class WorkflowStatus(str, enum.Enum):
    """Workflow status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TriggerType(str, enum.Enum):
    """Trigger type enumeration"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    EVENT = "event"
    API = "api"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflows = relationship("Workflow", back_populates="owner", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="triggered_by_user")


class Workflow(Base):
    """Workflow model - represents a business process"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT, index=True)
    definition = Column(JSON, nullable=False)  # Workflow definition (nodes, edges, etc.)
    version = Column(Integer, default=1)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(100), index=True)
    tags = Column(JSON)  # List of tags
    is_template = Column(Boolean, default=False)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="workflows")
    executions = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")
    triggers = relationship("Trigger", back_populates="workflow", cascade="all, delete-orphan")
    variables = relationship("WorkflowVariable", back_populates="workflow", cascade="all, delete-orphan")


class Execution(Base):
    """Execution model - represents a workflow execution instance"""
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    trigger_type = Column(SQLEnum(TriggerType), nullable=False)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"))
    input_data = Column(JSON)  # Input parameters
    output_data = Column(JSON)  # Output results
    context = Column(JSON)  # Execution context
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    triggered_by_user = relationship("User", back_populates="executions")
    tasks = relationship("TaskExecution", back_populates="execution", cascade="all, delete-orphan")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")


class TaskExecution(Base):
    """Task execution model - represents individual task execution within a workflow"""
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False, index=True)
    task_id = Column(String(100), nullable=False)  # Task ID from workflow definition
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(100), nullable=False)  # e.g., http_request, email, script, etc.
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("Execution", back_populates="tasks")


class Trigger(Base):
    """Trigger model - defines when a workflow should be executed"""
    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    trigger_type = Column(SQLEnum(TriggerType), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    configuration = Column(JSON, nullable=False)  # Trigger-specific config (cron, webhook URL, etc.)
    last_triggered_at = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow = relationship("Workflow", back_populates="triggers")


class WorkflowVariable(Base):
    """Workflow variable model - stores workflow-specific variables"""
    __tablename__ = "workflow_variables"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    is_secret = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow = relationship("Workflow", back_populates="variables")


class Integration(Base):
    """Integration model - external service connections"""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False, index=True)  # slack, email, http, database, etc.
    description = Column(Text)
    configuration = Column(JSON, nullable=False)  # Connection details
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Template(Base):
    """Template model - pre-built workflow templates"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)
    tags = Column(JSON)
    definition = Column(JSON, nullable=False)  # Workflow definition
    icon = Column(String(255))
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExecutionLog(Base):
    """Execution log model - detailed logs for workflow executions"""
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    task_id = Column(String(100))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    execution = relationship("Execution", back_populates="logs")


class Schedule(Base):
    """Schedule model - manages scheduled workflow executions"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    next_run_at = Column(DateTime)
    last_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit log model - tracks all system changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer)
    changes = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)