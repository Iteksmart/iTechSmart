"""
iTechSmart Workflow - Automation Orchestrator Models
Visual workflow builder with incident response and deployment automation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class NodeType(str, Enum):
    """Workflow node types"""

    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    DELAY = "delay"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    SCRIPT = "script"
    API_CALL = "api_call"
    DATABASE = "database"
    TRANSFORM = "transform"
    ERROR_HANDLER = "error_handler"


class TriggerType(str, Enum):
    """Workflow trigger types"""

    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    EVENT = "event"
    EMAIL = "email"
    FILE_WATCH = "file_watch"
    API_ENDPOINT = "api_endpoint"
    INCIDENT = "incident"
    ALERT = "alert"
    DEPLOYMENT = "deployment"


class ActionType(str, Enum):
    """Action types for automation"""

    # Incident Response
    CREATE_INCIDENT = "create_incident"
    UPDATE_INCIDENT = "update_incident"
    ASSIGN_INCIDENT = "assign_incident"
    ESCALATE_INCIDENT = "escalate_incident"
    RESOLVE_INCIDENT = "resolve_incident"

    # Deployment
    DEPLOY_APPLICATION = "deploy_application"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    RUN_TESTS = "run_tests"
    BACKUP_DATABASE = "backup_database"
    SCALE_SERVICE = "scale_service"

    # Infrastructure
    RESTART_SERVICE = "restart_service"
    EXECUTE_COMMAND = "execute_command"
    RUN_SCRIPT = "run_script"
    PROVISION_RESOURCE = "provision_resource"

    # Communication
    SEND_EMAIL = "send_email"
    SEND_SLACK = "send_slack"
    SEND_SMS = "send_sms"
    CREATE_TICKET = "create_ticket"

    # Data
    QUERY_DATABASE = "query_database"
    UPDATE_DATABASE = "update_database"
    CALL_API = "call_api"
    TRANSFORM_DATA = "transform_data"

    # Other
    WAIT = "wait"
    APPROVAL = "approval"
    CUSTOM = "custom"


class ExecutionStatus(str, Enum):
    """Execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Workflow status"""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# ============================================================================
# AUTOMATION ORCHESTRATOR MODELS
# ============================================================================


class AutomationWorkflow:
    """
    Enhanced workflow with visual builder support
    """

    def __init__(self, workflow_id: str, name: str, description: str, created_by: str):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.created_by = created_by
        self.status = WorkflowStatus.DRAFT
        self.version = 1
        self.category: Optional[str] = None
        self.tags: List[str] = []
        self.is_template = False
        self.is_public = False

        # Visual builder data
        self.canvas_data: Dict[str, Any] = {
            "nodes": [],
            "edges": [],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
        }

        # Workflow configuration
        self.triggers: List[Dict[str, Any]] = []
        self.variables: Dict[str, Any] = {}
        self.settings: Dict[str, Any] = {
            "timeout": 3600,
            "retry_on_failure": True,
            "max_retries": 3,
            "concurrent_executions": 1,
            "error_handling": "stop",
        }

        # Execution stats
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.average_duration: Optional[float] = None
        self.last_executed_at: Optional[datetime] = None

        # Metadata
        self.organization_id: Optional[str] = None
        self.folder_id: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.updated_by: Optional[str] = None


class WorkflowNode:
    """
    Visual workflow node
    """

    def __init__(self, node_id: str, workflow_id: str, node_type: NodeType, label: str):
        self.node_id = node_id
        self.workflow_id = workflow_id
        self.node_type = node_type
        self.label = label
        self.description: Optional[str] = None

        # Visual position
        self.position_x: float = 0
        self.position_y: float = 0

        # Node configuration
        self.config: Dict[str, Any] = {}
        self.input_schema: Dict[str, Any] = {}
        self.output_schema: Dict[str, Any] = {}

        # Connections
        self.input_connections: List[str] = []  # Node IDs
        self.output_connections: List[str] = []  # Node IDs

        # Execution settings
        self.timeout: Optional[int] = None
        self.retry_on_failure = False
        self.max_retries = 0
        self.continue_on_error = False

        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class WorkflowEdge:
    """
    Connection between workflow nodes
    """

    def __init__(
        self, edge_id: str, workflow_id: str, source_node_id: str, target_node_id: str
    ):
        self.edge_id = edge_id
        self.workflow_id = workflow_id
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.source_handle: Optional[str] = None  # Output handle
        self.target_handle: Optional[str] = None  # Input handle

        # Conditional edge
        self.condition: Optional[str] = None
        self.condition_type: Optional[str] = (
            None  # equals, contains, greater_than, etc.
        )

        # Visual styling
        self.label: Optional[str] = None
        self.style: Dict[str, Any] = {}

        # Metadata
        self.created_at = datetime.utcnow()


class WorkflowExecution:
    """
    Workflow execution instance
    """

    def __init__(self, execution_id: str, workflow_id: str, triggered_by: str):
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.triggered_by = triggered_by  # manual, schedule, webhook, etc.
        self.triggered_by_user: Optional[str] = None
        self.status = ExecutionStatus.PENDING

        # Execution data
        self.input_data: Dict[str, Any] = {}
        self.output_data: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}

        # Progress tracking
        self.current_node_id: Optional[str] = None
        self.completed_nodes: List[str] = []
        self.failed_nodes: List[str] = []
        self.skipped_nodes: List[str] = []

        # Timing
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.duration_seconds: Optional[float] = None

        # Error handling
        self.error_message: Optional[str] = None
        self.error_node_id: Optional[str] = None
        self.error_details: Dict[str, Any] = {}

        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class NodeExecution:
    """
    Individual node execution within workflow
    """

    def __init__(
        self,
        node_execution_id: str,
        execution_id: str,
        node_id: str,
        node_type: NodeType,
    ):
        self.node_execution_id = node_execution_id
        self.execution_id = execution_id
        self.node_id = node_id
        self.node_type = node_type
        self.status = ExecutionStatus.PENDING

        # Execution data
        self.input_data: Dict[str, Any] = {}
        self.output_data: Dict[str, Any] = {}
        self.logs: List[str] = []

        # Timing
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.duration_seconds: Optional[float] = None

        # Retry tracking
        self.attempt_number = 1
        self.max_attempts = 1

        # Error handling
        self.error_message: Optional[str] = None
        self.error_details: Dict[str, Any] = {}

        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class WorkflowTrigger:
    """
    Workflow trigger configuration
    """

    def __init__(
        self, trigger_id: str, workflow_id: str, trigger_type: TriggerType, name: str
    ):
        self.trigger_id = trigger_id
        self.workflow_id = workflow_id
        self.trigger_type = trigger_type
        self.name = name
        self.description: Optional[str] = None
        self.is_enabled = True

        # Trigger configuration
        self.config: Dict[str, Any] = {}

        # Schedule trigger
        self.schedule_cron: Optional[str] = None
        self.schedule_timezone: str = "UTC"

        # Webhook trigger
        self.webhook_url: Optional[str] = None
        self.webhook_secret: Optional[str] = None

        # Event trigger
        self.event_type: Optional[str] = None
        self.event_source: Optional[str] = None
        self.event_filters: Dict[str, Any] = {}

        # Execution stats
        self.trigger_count = 0
        self.last_triggered_at: Optional[datetime] = None

        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class WorkflowTemplate:
    """
    Pre-built workflow template
    """

    def __init__(self, template_id: str, name: str, description: str, category: str):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.category = category
        self.icon: Optional[str] = None
        self.tags: List[str] = []

        # Template data
        self.workflow_data: Dict[str, Any] = {}
        self.canvas_data: Dict[str, Any] = {}

        # Usage stats
        self.use_count = 0
        self.rating: Optional[float] = None

        # Metadata
        self.is_public = True
        self.created_by: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class IntegrationAction:
    """
    Pre-configured integration action
    """

    def __init__(
        self,
        action_id: str,
        integration_name: str,
        action_name: str,
        action_type: ActionType,
    ):
        self.action_id = action_id
        self.integration_name = integration_name
        self.action_name = action_name
        self.action_type = action_type
        self.description: Optional[str] = None
        self.icon: Optional[str] = None

        # Action configuration
        self.input_schema: Dict[str, Any] = {}
        self.output_schema: Dict[str, Any] = {}
        self.config_schema: Dict[str, Any] = {}

        # Authentication
        self.requires_auth = True
        self.auth_type: Optional[str] = None  # api_key, oauth, basic, etc.

        # Metadata
        self.category: Optional[str] = None
        self.tags: List[str] = []
        self.is_active = True
        self.created_at = datetime.utcnow()


class WorkflowVariable:
    """
    Workflow variable definition
    """

    def __init__(
        self, variable_id: str, workflow_id: str, name: str, variable_type: str
    ):
        self.variable_id = variable_id
        self.workflow_id = workflow_id
        self.name = name
        self.variable_type = variable_type  # string, number, boolean, object, array
        self.description: Optional[str] = None
        self.default_value: Any = None
        self.is_required = False
        self.is_sensitive = False
        self.validation_rules: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()


class WorkflowSchedule:
    """
    Workflow schedule configuration
    """

    def __init__(self, schedule_id: str, workflow_id: str, cron_expression: str):
        self.schedule_id = schedule_id
        self.workflow_id = workflow_id
        self.cron_expression = cron_expression
        self.timezone = "UTC"
        self.is_enabled = True
        self.description: Optional[str] = None

        # Execution window
        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None

        # Stats
        self.execution_count = 0
        self.last_execution_at: Optional[datetime] = None
        self.next_execution_at: Optional[datetime] = None

        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class WorkflowWebhook:
    """
    Workflow webhook endpoint
    """

    def __init__(self, webhook_id: str, workflow_id: str, endpoint_path: str):
        self.webhook_id = webhook_id
        self.workflow_id = workflow_id
        self.endpoint_path = endpoint_path
        self.is_enabled = True

        # Security
        self.secret_key: Optional[str] = None
        self.require_authentication = True
        self.allowed_ips: List[str] = []

        # Configuration
        self.http_method = "POST"
        self.content_type = "application/json"
        self.headers: Dict[str, str] = {}

        # Stats
        self.request_count = 0
        self.last_request_at: Optional[datetime] = None

        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class WorkflowLog:
    """
    Workflow execution log entry
    """

    def __init__(self, log_id: str, execution_id: str, level: str, message: str):
        self.log_id = log_id
        self.execution_id = execution_id
        self.level = level  # debug, info, warning, error
        self.message = message
        self.node_id: Optional[str] = None
        self.details: Dict[str, Any] = {}
        self.timestamp = datetime.utcnow()


class WorkflowMetrics:
    """
    Workflow performance metrics
    """

    def __init__(
        self,
        metric_id: str,
        workflow_id: str,
        period_start: datetime,
        period_end: datetime,
    ):
        self.metric_id = metric_id
        self.workflow_id = workflow_id
        self.period_start = period_start
        self.period_end = period_end

        # Execution metrics
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.cancelled_executions = 0

        # Performance metrics
        self.average_duration: Optional[float] = None
        self.min_duration: Optional[float] = None
        self.max_duration: Optional[float] = None
        self.p95_duration: Optional[float] = None
        self.p99_duration: Optional[float] = None

        # Success rate
        self.success_rate: float = 0.0

        # Node metrics
        self.node_execution_counts: Dict[str, int] = {}
        self.node_failure_counts: Dict[str, int] = {}

        # Metadata
        self.created_at = datetime.utcnow()
