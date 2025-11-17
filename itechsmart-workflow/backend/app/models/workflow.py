"""
iTechSmart Workflow - Database Models
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    JSON,
    Text,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow status enumeration"""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    """Execution status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow:
    """Workflow definition model"""

    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    # Workflow definition
    nodes = Column(JSON, nullable=False)  # List of workflow nodes
    edges = Column(JSON, nullable=False)  # List of connections between nodes
    triggers = Column(JSON)  # List of workflow triggers

    # Metadata
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False)

    # Ownership
    created_by = Column(String(36))
    organization_id = Column(String(36))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow")
    tasks = relationship("WorkflowTask", back_populates="workflow")


class WorkflowExecution:
    """Workflow execution instance model"""

    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)

    # Execution data
    input_data = Column(JSON)
    context = Column(JSON)
    output_data = Column(JSON)

    # Status tracking
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    current_node_id = Column(String(36))
    completed_nodes = Column(JSON)  # List of completed node IDs
    failed_nodes = Column(JSON)  # List of failed node IDs

    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Metadata
    triggered_by = Column(String(100))  # manual, schedule, webhook, etc.
    triggered_by_user_id = Column(String(36))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    tasks = relationship("WorkflowTask", back_populates="execution")


class WorkflowTask:
    """Individual task within a workflow execution"""

    __tablename__ = "workflow_tasks"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    execution_id = Column(String(36), ForeignKey("workflow_executions.id"))

    # Task details
    node_id = Column(String(36), nullable=False)
    task_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Assignment
    assigned_to = Column(String(36))
    assigned_at = Column(DateTime)

    # Status
    status = Column(
        String(50), default="pending"
    )  # pending, in_progress, completed, failed
    priority = Column(String(20), default="medium")  # low, medium, high, urgent

    # Data
    input_data = Column(JSON)
    output_data = Column(JSON)

    # Timing
    due_date = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow = relationship("Workflow", back_populates="tasks")
    execution = relationship("WorkflowExecution", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task")


class TaskComment:
    """Comments on workflow tasks"""

    __tablename__ = "task_comments"

    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("workflow_tasks.id"), nullable=False)

    # Comment details
    comment = Column(Text, nullable=False)
    author_id = Column(String(36), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task = relationship("WorkflowTask", back_populates="comments")


class WorkflowTemplate:
    """Pre-built workflow templates"""

    __tablename__ = "workflow_templates"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    # Template definition
    nodes = Column(JSON, nullable=False)
    edges = Column(JSON, nullable=False)

    # Metadata
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Integer)

    # Tags for searchability
    tags = Column(JSON)

    # Ownership
    created_by = Column(String(36))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowTrigger:
    """Workflow trigger configurations"""

    __tablename__ = "workflow_triggers"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)

    # Trigger configuration
    trigger_type = Column(
        String(50), nullable=False
    )  # schedule, webhook, event, manual
    trigger_config = Column(JSON, nullable=False)

    # Status
    is_active = Column(Boolean, default=True)

    # Statistics
    trigger_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApprovalRequest:
    """Approval requests within workflows"""

    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True)
    execution_id = Column(
        String(36), ForeignKey("workflow_executions.id"), nullable=False
    )
    node_id = Column(String(36), nullable=False)

    # Approval details
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Approvers
    approvers = Column(JSON, nullable=False)  # List of user IDs
    required_approvals = Column(Integer, default=1)

    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected

    # Responses
    approvals = Column(JSON)  # List of approval responses

    # Timing
    due_date = Column(DateTime)
    responded_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowMetrics:
    """Workflow performance metrics"""

    __tablename__ = "workflow_metrics"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)

    # Execution metrics
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    cancelled_executions = Column(Integer, default=0)

    # Performance metrics
    avg_duration_seconds = Column(Integer)
    min_duration_seconds = Column(Integer)
    max_duration_seconds = Column(Integer)

    # Success rate
    success_rate = Column(Integer)  # Percentage

    # Last execution
    last_execution_at = Column(DateTime)
    last_execution_status = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
