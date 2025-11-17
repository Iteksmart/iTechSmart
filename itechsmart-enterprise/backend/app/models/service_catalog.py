"""
iTechSmart Enterprise - Service Catalog Models
Self-service portal with ITIL alignment
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum


class ServiceCategory(str, Enum):
    """Service catalog categories"""

    ACCESS_REQUEST = "access_request"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    INFRASTRUCTURE = "infrastructure"
    SUPPORT = "support"
    TRAINING = "training"
    CONSULTING = "consulting"
    OTHER = "other"


class RequestStatus(str, Enum):
    """Service request status"""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class RequestPriority(str, Enum):
    """Request priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    """Approval status"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class FulfillmentStatus(str, Enum):
    """Fulfillment task status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# SERVICE CATALOG MODELS
# ============================================================================


class ServiceCatalogItem:
    """
    Service catalog item definition
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        category: ServiceCategory,
        owner: str,
    ):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.category = category
        self.owner = owner
        self.short_description: Optional[str] = None
        self.icon: Optional[str] = None
        self.is_active = True
        self.is_visible = True
        self.requires_approval = True
        self.auto_fulfill = False
        self.estimated_delivery_days: Optional[int] = None
        self.cost: float = 0.0
        self.cost_center: Optional[str] = None
        self.tags: List[str] = []
        self.prerequisites: List[str] = []
        self.documentation_url: Optional[str] = None
        self.support_group: Optional[str] = None
        self.sla_id: Optional[str] = None
        self.form_fields: List[dict] = []  # Custom form fields
        self.approval_chain: List[str] = []  # List of approver IDs
        self.fulfillment_workflow: Optional[str] = None
        self.request_count = 0
        self.average_fulfillment_time: Optional[float] = None
        self.satisfaction_score: Optional[float] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.created_by: Optional[str] = None
        self.updated_by: Optional[str] = None


class ServiceRequest:
    """
    Service request submitted by user
    """

    def __init__(
        self,
        request_id: str,
        item_id: str,
        requester_id: str,
        requester_name: str,
        requester_email: str,
    ):
        self.request_id = request_id
        self.item_id = item_id
        self.requester_id = requester_id
        self.requester_name = requester_name
        self.requester_email = requester_email
        self.status = RequestStatus.DRAFT
        self.priority = RequestPriority.MEDIUM
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.justification: Optional[str] = None
        self.form_data: dict = {}  # User-submitted form data
        self.requested_for: Optional[str] = None  # If requesting for someone else
        self.cost_center: Optional[str] = None
        self.estimated_cost: float = 0.0
        self.actual_cost: float = 0.0
        self.submitted_at: Optional[datetime] = None
        self.approved_at: Optional[datetime] = None
        self.fulfilled_at: Optional[datetime] = None
        self.closed_at: Optional[datetime] = None
        self.due_date: Optional[datetime] = None
        self.assigned_to: Optional[str] = None
        self.assigned_group: Optional[str] = None
        self.fulfillment_notes: Optional[str] = None
        self.cancellation_reason: Optional[str] = None
        self.satisfaction_rating: Optional[int] = None  # 1-5
        self.satisfaction_comment: Optional[str] = None
        self.sla_breached = False
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ServiceApproval:
    """
    Approval step for service request
    """

    def __init__(
        self,
        approval_id: str,
        request_id: str,
        approver_id: str,
        approver_name: str,
        sequence: int,
    ):
        self.approval_id = approval_id
        self.request_id = request_id
        self.approver_id = approver_id
        self.approver_name = approver_name
        self.sequence = sequence  # Order in approval chain
        self.status = ApprovalStatus.PENDING
        self.decision: Optional[str] = None  # approved, rejected
        self.comments: Optional[str] = None
        self.decided_at: Optional[datetime] = None
        self.notified_at: Optional[datetime] = None
        self.reminder_sent_at: Optional[datetime] = None
        self.due_date: Optional[datetime] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class FulfillmentTask:
    """
    Task for fulfilling service request
    """

    def __init__(self, task_id: str, request_id: str, title: str, assigned_to: str):
        self.task_id = task_id
        self.request_id = request_id
        self.title = title
        self.description: Optional[str] = None
        self.assigned_to = assigned_to
        self.assigned_group: Optional[str] = None
        self.status = FulfillmentStatus.PENDING
        self.sequence = 0  # Order in fulfillment workflow
        self.depends_on: List[str] = []  # Task dependencies
        self.estimated_hours: Optional[float] = None
        self.actual_hours: Optional[float] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.due_date: Optional[datetime] = None
        self.notes: Optional[str] = None
        self.checklist: List[dict] = []  # Checklist items
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ServiceSLA:
    """
    Service Level Agreement definition
    """

    def __init__(self, sla_id: str, name: str, description: str):
        self.sla_id = sla_id
        self.name = name
        self.description = description
        self.is_active = True
        # Response times (in hours)
        self.response_time_low: Optional[int] = 24
        self.response_time_medium: Optional[int] = 8
        self.response_time_high: Optional[int] = 4
        self.response_time_critical: Optional[int] = 1
        # Resolution times (in hours)
        self.resolution_time_low: Optional[int] = 120
        self.resolution_time_medium: Optional[int] = 48
        self.resolution_time_high: Optional[int] = 24
        self.resolution_time_critical: Optional[int] = 8
        # Business hours
        self.business_hours_start = "09:00"
        self.business_hours_end = "17:00"
        self.business_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        self.exclude_holidays = True
        # Metrics
        self.target_fulfillment_rate: float = 95.0  # Percentage
        self.target_satisfaction_score: float = 4.0  # Out of 5
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ServiceCostCenter:
    """
    Cost center for service requests
    """

    def __init__(self, cost_center_id: str, name: str, code: str, manager: str):
        self.cost_center_id = cost_center_id
        self.name = name
        self.code = code
        self.manager = manager
        self.description: Optional[str] = None
        self.budget: float = 0.0
        self.spent: float = 0.0
        self.is_active = True
        self.department: Optional[str] = None
        self.location: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class RequestWorkflow:
    """
    Workflow definition for service requests
    """

    def __init__(self, workflow_id: str, name: str, item_id: str):
        self.workflow_id = workflow_id
        self.name = name
        self.item_id = item_id
        self.description: Optional[str] = None
        self.is_active = True
        self.steps: List[dict] = []  # Workflow steps
        self.approval_required = True
        self.auto_assign = False
        self.notification_template: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class RequestComment:
    """
    Comment on service request
    """

    def __init__(
        self,
        comment_id: str,
        request_id: str,
        user_id: str,
        user_name: str,
        comment: str,
    ):
        self.comment_id = comment_id
        self.request_id = request_id
        self.user_id = user_id
        self.user_name = user_name
        self.comment = comment
        self.is_internal = False  # Internal vs customer-facing
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class RequestAttachment:
    """
    File attachment for service request
    """

    def __init__(
        self,
        attachment_id: str,
        request_id: str,
        filename: str,
        file_path: str,
        uploaded_by: str,
    ):
        self.attachment_id = attachment_id
        self.request_id = request_id
        self.filename = filename
        self.file_path = file_path
        self.uploaded_by = uploaded_by
        self.file_size: Optional[int] = None
        self.mime_type: Optional[str] = None
        self.description: Optional[str] = None
        self.created_at = datetime.utcnow()


class ServiceMetrics:
    """
    Service catalog metrics and KPIs
    """

    def __init__(
        self, metric_id: str, item_id: str, period_start: datetime, period_end: datetime
    ):
        self.metric_id = metric_id
        self.item_id = item_id
        self.period_start = period_start
        self.period_end = period_end
        self.total_requests = 0
        self.fulfilled_requests = 0
        self.rejected_requests = 0
        self.cancelled_requests = 0
        self.average_fulfillment_time: Optional[float] = None  # Hours
        self.average_approval_time: Optional[float] = None  # Hours
        self.sla_compliance_rate: float = 0.0  # Percentage
        self.average_satisfaction_score: Optional[float] = None
        self.total_cost: float = 0.0
        self.created_at = datetime.utcnow()
