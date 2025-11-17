"""
Database models for iTechSmart Ninja
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Enum,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles"""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class TaskStatus(str, enum.Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    api_key = Column(String, unique=True, index=True)

    # Gamification
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    achievements = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class APIKey(Base):
    """API Keys for external services (encrypted)"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # openai, anthropic, google, etc.
    key_name = Column(String, nullable=False)
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="api_keys")


class UserSettings(Base):
    """User-specific settings"""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # AI Preferences
    default_ai_provider = Column(String, default="openai")
    default_model = Column(String, default="gpt-4")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)

    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)

    # UI Preferences
    theme = Column(String, default="light")
    language = Column(String, default="en")

    # Other settings
    settings_json = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")


class Task(Base):
    """Task/Job execution model"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Task details
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(String)  # research, code, website, analysis, etc.
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    # Execution details
    agent_type = Column(String)  # researcher, coder, writer, analyst, etc.
    ai_provider = Column(String)
    ai_model = Column(String)

    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100
    current_step = Column(String)
    total_steps = Column(Integer)

    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    artifacts = Column(JSON, default=list)  # Generated files, URLs, etc.

    # Execution metadata
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_time = Column(Float)  # seconds

    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tasks")
    steps = relationship(
        "TaskStep", back_populates="task", cascade="all, delete-orphan"
    )


class TaskStep(Base):
    """Individual steps within a task"""

    __tablename__ = "task_steps"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    step_number = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    # Step execution
    agent_used = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)

    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_time = Column(Float)

    # Error handling
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="steps")


class Template(Base):
    """Automation templates"""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # infrastructure, security, cost, incident, backup

    # Template definition
    template_data = Column(JSON, nullable=False)
    variables = Column(JSON, default=list)

    # Metadata
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    # Author
    created_by = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Achievement(Base):
    """Gamification achievements"""

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)
    points = Column(Integer, default=0)

    # Unlock criteria
    criteria_type = Column(String)  # tasks_completed, code_generated, etc.
    criteria_value = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """Audit log for all actions"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(Integer)
    details = Column(JSON)

    ip_address = Column(String)
    user_agent = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chart(Base):
    """Data visualization charts"""

    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Chart configuration
    chart_id = Column(String, unique=True, index=True, nullable=False)
    chart_type = Column(String, nullable=False)  # bar, line, pie, scatter, etc.
    title = Column(String, nullable=False)
    description = Column(Text)

    # Chart data and options
    data = Column(JSON, nullable=False)  # Chart data
    options = Column(JSON)  # Chart options (colors, theme, etc.)

    # Metadata
    is_public = Column(Boolean, default=False)
    tags = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class Dashboard(Base):
    """Interactive dashboards with multiple charts"""

    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Dashboard configuration
    dashboard_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)

    # Layout configuration
    layout = Column(JSON)  # Dashboard layout (columns, spacing, etc.)
    chart_ids = Column(JSON, default=list)  # List of chart IDs in dashboard

    # Metadata
    is_public = Column(Boolean, default=False)
    tags = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class Document(Base):
    """Uploaded documents for processing"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File information
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, xlsx, etc.
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # in bytes

    # Processing results
    page_count = Column(Integer)
    extracted_text = Column(Text)
    metadata = Column(JSON)

    # Status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")
    tables = relationship(
        "DocumentTable", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentTable(Base):
    """Extracted tables from documents"""

    __tablename__ = "document_tables"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Table information
    page_number = Column(Integer)
    table_number = Column(Integer)
    table_data = Column(JSON, nullable=False)  # Table data as JSON

    # Metadata
    rows = Column(Integer)
    columns = Column(Integer)

    # Timestamps
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="tables")


class VirtualMachine(Base):
    """Virtual machines for concurrent execution"""

    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # VM configuration
    vm_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    language = Column(String, nullable=False)  # python, nodejs, java, etc.
    status = Column(String, default="stopped")  # running, stopped, error

    # Container information
    container_id = Column(String)

    # Resource limits
    cpu_limit = Column(Float, default=1.0)  # CPU cores
    memory_limit = Column(Integer, default=512)  # MB
    disk_limit = Column(Integer, default=1024)  # MB

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    stopped_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")
    executions = relationship(
        "VMExecution", back_populates="vm", cascade="all, delete-orphan"
    )


class VMExecution(Base):
    """VM code execution history"""

    __tablename__ = "vm_executions"

    id = Column(Integer, primary_key=True, index=True)
    vm_id = Column(Integer, ForeignKey("virtual_machines.id"), nullable=False)

    # Execution details
    code = Column(Text, nullable=False)
    output = Column(Text)
    error = Column(Text)
    exit_code = Column(Integer, default=0)

    # Performance
    execution_time = Column(Float)  # seconds

    # Timestamp
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    vm = relationship("VirtualMachine", back_populates="executions")


class ScheduledTask(Base):
    """Scheduled tasks for automated execution"""

    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Task configuration
    task_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    schedule = Column(String, nullable=False)  # Cron expression or interval

    # Code to execute
    code = Column(Text, nullable=False)
    language = Column(String, default="python")

    # Status
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True))
    last_status = Column(String)  # success, failure, running

    # Retry configuration
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout = Column(Integer, default=300)  # seconds

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    executions = relationship(
        "TaskExecution", back_populates="task", cascade="all, delete-orphan"
    )


class TaskExecution(Base):
    """Task execution history"""

    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("scheduled_tasks.id"), nullable=False)

    # Execution details
    execution_id = Column(String, unique=True, index=True)
    status = Column(String, nullable=False)  # success, failure, running, timeout
    output = Column(Text)
    error = Column(Text)
    exit_code = Column(Integer, default=0)

    # Performance
    execution_time = Column(Float)  # seconds

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    task = relationship("ScheduledTask", back_populates="executions")


class MCPDataSource(Base):
    """MCP data source configuration"""

    __tablename__ = "mcp_data_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Source configuration
    name = Column(String, nullable=False)
    type = Column(
        String, nullable=False
    )  # postgresql, mysql, mongodb, redis, rest_api, etc.
    connection_string = Column(String)  # Encrypted connection string
    config = Column(JSON)  # Additional configuration

    # Status
    enabled = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    queries = relationship(
        "MCPQuery", back_populates="source", cascade="all, delete-orphan"
    )


class MCPQuery(Base):
    """MCP query execution history"""

    __tablename__ = "mcp_queries"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("mcp_data_sources.id"), nullable=False)

    # Query details
    query = Column(Text, nullable=False)
    result = Column(JSON)  # Query result
    cached = Column(Boolean, default=False)

    # Performance
    execution_time = Column(Float)  # seconds

    # Timestamp
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source = relationship("MCPDataSource", back_populates="queries")


class ActionHistory(Base):
    """Action history for undo/redo functionality"""

    __tablename__ = "action_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Action details
    action_id = Column(String, unique=True, index=True, nullable=False)
    action_type = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # State information
    previous_state = Column(JSON)
    new_state = Column(JSON)
    metadata = Column(JSON)

    # Status
    undoable = Column(Boolean, default=True)
    undone = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class DebugSession(Base):
    """Debug session tracking"""

    __tablename__ = "debug_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session details
    session_type = Column(String, nullable=False)  # breakpoint, profile, analysis
    data = Column(JSON)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class Workflow(Base):
    """Workflow definitions"""

    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Workflow details
    workflow_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    definition = Column(JSON, nullable=False)
    version = Column(Integer, default=1)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class WorkflowExecution(Base):
    """Workflow execution history"""

    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workflow_id = Column(String, nullable=False)

    # Execution details
    execution_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    context = Column(JSON)
    logs = Column(JSON)
    error = Column(Text)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")


class Team(Base):
    """Team for collaboration"""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String, default="free")  # free, pro, enterprise

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User")


class TeamMember(Base):
    """Team membership"""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # owner, admin, member, viewer
    status = Column(String, default="active")  # active, inactive

    # Timestamp
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class Workspace(Base):
    """Team workspace"""

    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, unique=True, index=True, nullable=False)
    team_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User")


class Comment(Base):
    """Comments on resources"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String, nullable=False)  # code, file, task, workflow
    resource_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    team_id = Column(Integer)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class VideoGeneration(Base):
    """Video generation history"""

    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Video details
    video_id = Column(String, unique=True, index=True)
    prompt = Column(Text, nullable=False)
    provider = Column(String, nullable=False)

    # Video properties
    duration = Column(Integer)  # seconds
    resolution = Column(String)  # 720p, 1080p, 4k
    video_url = Column(String)

    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed

    # Metadata
    metadata = Column(JSON)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
