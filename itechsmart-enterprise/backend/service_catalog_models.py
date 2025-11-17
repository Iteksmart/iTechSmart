"""
iTechSmart Service Catalog - Enhanced Database Models
Comprehensive self-service portal with AI automation
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class ServiceCategory(enum.Enum):
    """Service catalog categories"""

    ACCESS_MANAGEMENT = "access_management"
    IT_SUPPORT = "it_support"
    SYSTEMS_SERVERS = "systems_servers"
    DEVOPS_AUTOMATION = "devops_automation"
    NETWORK_REQUESTS = "network_requests"
    SOFTWARE_DEPLOYMENT = "software_deployment"
    HARDWARE_REQUESTS = "hardware_requests"
    HR_ONBOARDING = "hr_onboarding"


class RequestStatus(enum.Enum):
    """Request status"""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ApprovalStatus(enum.Enum):
    """Approval status"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class AutomationType(enum.Enum):
    """Automation execution type"""

    POWERSHELL = "powershell"
    BASH = "bash"
    SSH = "ssh"
    PYTHON = "python"
    API_CALL = "api_call"
    WEBHOOK = "webhook"
    AI_AGENT = "ai_agent"


class ServiceItem(Base):
    """Service catalog items"""

    __tablename__ = "service_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(ServiceCategory), nullable=False, index=True)
    icon = Column(String(50))  # Icon name for UI

    # Configuration
    form_schema = Column(JSON)  # Dynamic form fields
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    auto_fulfill = Column(Boolean, default=False)

    # SLA
    sla_hours = Column(Integer, default=24)
    priority = Column(Integer, default=3)  # 1=Critical, 5=Low

    # Automation
    automation_enabled = Column(Boolean, default=False)
    automation_script = Column(Text)  # Script content
    automation_type = Column(SQLEnum(AutomationType))
    ai_assisted = Column(Boolean, default=False)

    # Workflow
    approval_workflow = Column(JSON)  # List of approval steps
    fulfillment_workflow = Column(JSON)  # List of fulfillment steps

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    requests = relationship("ServiceRequest", back_populates="service_item")


class ServiceRequest(Base):
    """Service requests from users"""

    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, index=True)

    # Service
    service_item_id = Column(Integer, ForeignKey("service_items.id"), nullable=False)

    # Requester
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_email = Column(String(255))
    requester_name = Column(String(200))

    # Request details
    form_data = Column(JSON)  # User-submitted form data
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.SUBMITTED, index=True)
    priority = Column(Integer, default=3)

    # Approval
    requires_approval = Column(Boolean, default=True)
    current_approval_step = Column(Integer, default=0)

    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime)

    # Automation
    automation_executed = Column(Boolean, default=False)
    automation_result = Column(JSON)
    ai_suggestions = Column(JSON)

    # Timing
    submitted_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    due_date = Column(DateTime)

    # Notes
    notes = Column(Text)
    resolution_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_item = relationship("ServiceItem", back_populates="requests")
    approvals = relationship(
        "RequestApproval", back_populates="request", cascade="all, delete-orphan"
    )
    activities = relationship(
        "RequestActivity", back_populates="request", cascade="all, delete-orphan"
    )
    automations = relationship(
        "RequestAutomation", back_populates="request", cascade="all, delete-orphan"
    )


class RequestApproval(Base):
    """Approval workflow for requests"""

    __tablename__ = "request_approvals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)

    # Approval step
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(200))

    # Approver
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_email = Column(String(255))
    approver_name = Column(String(200))

    # Status
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)

    # Decision
    decision_notes = Column(Text)
    decided_at = Column(DateTime)

    # Timing
    requested_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    request = relationship("ServiceRequest", back_populates="approvals")


class RequestActivity(Base):
    """Activity log for requests"""

    __tablename__ = "request_activities"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)

    # Activity
    activity_type = Column(String(50), index=True)  # created, updated, approved, etc.
    description = Column(Text)

    # Actor
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String(200))

    # Details
    old_value = Column(JSON)
    new_value = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    request = relationship("ServiceRequest", back_populates="activities")


class RequestAutomation(Base):
    """Automation execution for requests"""

    __tablename__ = "request_automations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)

    # Automation
    automation_type = Column(SQLEnum(AutomationType), nullable=False)
    script_content = Column(Text)

    # Execution
    status = Column(String(50), default="pending", index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Results
    success = Column(Boolean, default=False)
    output = Column(Text)
    error = Column(Text)
    execution_time = Column(Integer)  # seconds

    # AI
    ai_assisted = Column(Boolean, default=False)
    ai_suggestions = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    request = relationship("ServiceRequest", back_populates="automations")


class WorkflowTemplate(Base):
    """Reusable workflow templates"""

    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Template
    template_type = Column(String(50))  # approval, fulfillment, automation
    steps = Column(JSON)  # List of workflow steps

    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))


class ServiceMetrics(Base):
    """Service catalog metrics and analytics"""

    __tablename__ = "service_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Service
    service_item_id = Column(Integer, ForeignKey("service_items.id"))

    # Metrics
    date = Column(DateTime, default=datetime.utcnow, index=True)
    total_requests = Column(Integer, default=0)
    completed_requests = Column(Integer, default=0)
    avg_completion_time = Column(Integer)  # hours
    avg_approval_time = Column(Integer)  # hours
    automation_success_rate = Column(Integer)  # percentage
    user_satisfaction = Column(Integer)  # 1-5 rating

    # SLA
    sla_met = Column(Integer, default=0)
    sla_breached = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationTemplate(Base):
    """Notification templates for service catalog"""

    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    event_type = Column(String(100), index=True)  # request_submitted, approved, etc.

    # Template
    subject = Column(String(500))
    body = Column(Text)

    # Configuration
    is_active = Column(Boolean, default=True)
    send_email = Column(Boolean, default=True)
    send_slack = Column(Boolean, default=False)
    send_teams = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
