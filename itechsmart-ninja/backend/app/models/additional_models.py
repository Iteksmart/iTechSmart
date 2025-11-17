"""
Additional Database Models for Features 6-15
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


# Feature 6: Data Visualization
class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chart_type = Column(String)  # bar, line, pie, scatter, etc.
    title = Column(String)
    data = Column(JSON)  # Chart data
    options = Column(JSON)  # Chart options (colors, theme, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="charts")


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    layout = Column(JSON)  # Dashboard layout configuration
    chart_ids = Column(JSON)  # List of chart IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="dashboards")


# Feature 7: Document Processing
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_type = Column(String)  # pdf, docx, xlsx, etc.
    file_path = Column(String)
    file_size = Column(Integer)  # bytes
    page_count = Column(Integer)
    extracted_text = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    user = relationship("User", back_populates="documents")
    tables = relationship("DocumentTable", back_populates="document")


class DocumentTable(Base):
    __tablename__ = "document_tables"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    page_number = Column(Integer)
    table_data = Column(JSON)  # Table data as JSON
    extracted_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="tables")


# Feature 8: Concurrent VMs
class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    status = Column(String)  # running, stopped, error
    language = Column(String)  # python, nodejs, java, go, rust
    container_id = Column(String)
    cpu_limit = Column(Float)  # CPU cores
    memory_limit = Column(Integer)  # MB
    disk_limit = Column(Integer)  # MB
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)

    user = relationship("User", back_populates="virtual_machines")
    executions = relationship("VMExecution", back_populates="vm")


class VMExecution(Base):
    __tablename__ = "vm_executions"

    id = Column(Integer, primary_key=True, index=True)
    vm_id = Column(Integer, ForeignKey("virtual_machines.id"))
    code = Column(Text)
    output = Column(Text)
    error = Column(Text)
    exit_code = Column(Integer)
    execution_time = Column(Float)  # seconds
    executed_at = Column(DateTime, default=datetime.utcnow)

    vm = relationship("VirtualMachine", back_populates="executions")


# Feature 9: Scheduled Tasks
class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    schedule = Column(String)  # Cron expression
    code = Column(Text)
    language = Column(String)
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout = Column(Integer)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scheduled_tasks")
    executions = relationship("TaskExecution", back_populates="task")


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("scheduled_tasks.id"))
    status = Column(String)  # success, failure, running
    output = Column(Text)
    error = Column(Text)
    execution_time = Column(Float)  # seconds
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    task = relationship("ScheduledTask", back_populates="executions")


# Feature 10: MCP Data Sources
class MCPDataSource(Base):
    __tablename__ = "mcp_data_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    type = Column(String)  # database, api, filesystem, search, queue
    connection_string = Column(String)  # Encrypted
    config = Column(JSON)
    enabled = Column(Boolean, default=True)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mcp_sources")
    queries = relationship("MCPQuery", back_populates="source")


class MCPQuery(Base):
    __tablename__ = "mcp_queries"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("mcp_data_sources.id"))
    query = Column(Text)
    result = Column(JSON)
    cached = Column(Boolean, default=False)
    execution_time = Column(Float)  # seconds
    executed_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("MCPDataSource", back_populates="queries")


# Feature 11: Undo/Redo
class ActionHistory(Base):
    __tablename__ = "action_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String)  # code_generation, file_modification, etc.
    action_data = Column(JSON)
    previous_state = Column(JSON)
    new_state = Column(JSON)
    undoable = Column(Boolean, default=True)
    undone = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="action_history")


# Feature 12: Video Generation
class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt = Column(Text)
    provider = Column(String)  # runway, stability, pika
    duration = Column(Integer)  # seconds
    resolution = Column(String)  # 720p, 1080p, 4k
    style = Column(String)
    status = Column(String)  # processing, completed, failed
    video_url = Column(String)
    cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="video_generations")


# Feature 14: Custom Workflows
class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    steps = Column(JSON)  # Workflow steps configuration
    version = Column(Integer, default=1)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    status = Column(String)  # running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    current_step = Column(Integer, default=0)
    input_data = Column(JSON)
    results = Column(JSON)
    error = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    workflow = relationship("Workflow", back_populates="executions")


# Feature 15: Team Collaboration
class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    plan = Column(String, default="free")  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team")
    workspaces = relationship("Workspace", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # owner, admin, member, viewer
    joined_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="members")
    user = relationship("User")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    name = Column(String)
    description = Column(Text)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="workspaces")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_type = Column(String)  # code, file, task, workflow
    resource_id = Column(Integer)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class TeamActivity(Base):
    __tablename__ = "team_activity"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)  # created, updated, deleted, etc.
    resource_type = Column(String)
    resource_id = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team")
    user = relationship("User")
