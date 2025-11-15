"""
Database models for iTechSmart Think-Tank
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class ProjectStatus(str, enum.Enum):
    """Status of a project"""
    IDEATION = "ideation"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class ProjectPriority(str, enum.Enum):
    """Priority level of a project"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class UserRole(str, enum.Enum):
    """User role in the system"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    PROJECT_MANAGER = "project_manager"
    CLIENT = "client"
    GUEST = "guest"


class MessageType(str, enum.Enum):
    """Type of chat message"""
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    CODE = "code"
    SYSTEM = "system"


class TaskStatus(str, enum.Enum):
    """Status of a task"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class AIRequestType(str, enum.Enum):
    """Type of AI request"""
    CODE_GENERATION = "code_generation"
    APP_SCAFFOLDING = "app_scaffolding"
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    role = Column(SQLEnum(UserRole), default=UserRole.DEVELOPER)
    avatar_url = Column(String(500))
    bio = Column(Text)
    skills = Column(JSON)  # List of skills
    
    # Status
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime)
    
    # Organization
    organization = Column(String(200))
    is_external = Column(Boolean, default=False)  # External client/guest
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects_created = relationship("Project", back_populates="creator", foreign_keys="Project.creator_id")
    team_memberships = relationship("TeamMember", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    tasks_assigned = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    ai_requests = relationship("AIRequest", back_populates="requester")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.IDEATION)
    priority = Column(SQLEnum(ProjectPriority), default=ProjectPriority.MEDIUM)
    progress = Column(Float, default=0.0)  # 0-100%
    
    # Details
    requirements = Column(JSON)  # List of requirements
    tech_stack = Column(JSON)  # Technologies to use
    estimated_hours = Column(Float)
    actual_hours = Column(Float, default=0.0)
    budget = Column(Float)
    
    # Dates
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Client info
    client_name = Column(String(200))
    client_organization = Column(String(200))
    client_email = Column(String(255))
    
    # Integration
    deployed_to_suite = Column(Boolean, default=False)
    suite_product_id = Column(String(100))  # ID in suite if deployed
    repository_url = Column(String(500))
    
    # Creator
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="projects_created", foreign_keys=[creator_id])
    team_members = relationship("TeamMember", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    messages = relationship("Message", back_populates="project")
    ai_requests = relationship("AIRequest", back_populates="project")
    progress_updates = relationship("ProgressUpdate", back_populates="project")
    files = relationship("ProjectFile", back_populates="project")


class TeamMember(Base):
    """Team member association"""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Role in project
    role = Column(String(100))  # Developer, Designer, PM, etc.
    permissions = Column(JSON)  # List of permissions
    
    # Status
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="team_members")
    user = relationship("User", back_populates="team_memberships")


class Message(Base):
    """Chat message model"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    
    # Attachments
    attachments = Column(JSON)  # List of file URLs
    
    # Thread
    parent_message_id = Column(Integer, ForeignKey("messages.id"))
    thread_count = Column(Integer, default=0)
    
    # Reactions
    reactions = Column(JSON)  # {emoji: [user_ids]}
    
    # Status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Mentions
    mentions = Column(JSON)  # List of user IDs mentioned
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="messages")
    sender = relationship("User", back_populates="messages")


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SQLEnum(ProjectPriority), default=ProjectPriority.MEDIUM)
    
    # Assignment
    assignee_id = Column(Integer, ForeignKey("users.id"))
    
    # Estimates
    estimated_hours = Column(Float)
    actual_hours = Column(Float, default=0.0)
    
    # Dates
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Dependencies
    depends_on = Column(JSON)  # List of task IDs
    blocks = Column(JSON)  # List of task IDs
    
    # Metadata
    tags = Column(JSON)
    checklist = Column(JSON)  # List of subtasks
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assignee_id])


class AIRequest(Base):
    """AI request model for SuperNinja Agent"""
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request details
    request_type = Column(SQLEnum(AIRequestType), nullable=False)
    prompt = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context
    
    # Response
    response = Column(Text)
    generated_code = Column(Text)
    generated_files = Column(JSON)  # List of generated files
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    
    # Execution
    execution_time_seconds = Column(Float)
    tokens_used = Column(Integer)
    
    # Result
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="ai_requests")
    requester = relationship("User", back_populates="ai_requests")


class ProgressUpdate(Base):
    """Progress update model"""
    __tablename__ = "progress_updates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Update details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    progress_percentage = Column(Float)  # Overall project progress at this point
    
    # Metrics
    tasks_completed = Column(Integer)
    tasks_total = Column(Integer)
    hours_spent = Column(Float)
    
    # Milestones
    is_milestone = Column(Boolean, default=False)
    milestone_name = Column(String(200))
    
    # Visibility
    visible_to_client = Column(Boolean, default=True)
    
    # Attachments
    attachments = Column(JSON)  # Screenshots, files, etc.
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="progress_updates")


class ProjectFile(Base):
    """Project file model"""
    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # File details
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # bytes
    file_type = Column(String(100))
    mime_type = Column(String(100))
    
    # Category
    category = Column(String(100))  # design, code, documentation, etc.
    
    # Metadata
    description = Column(Text)
    tags = Column(JSON)
    
    # Upload info
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="files")


class IdeaBoard(Base):
    """Idea board for brainstorming"""
    __tablename__ = "idea_boards"

    id = Column(Integer, primary_key=True, index=True)
    
    # Idea details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    
    # Status
    status = Column(String(50), default="proposed")  # proposed, discussing, approved, rejected, implemented
    
    # Voting
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
    # Implementation
    implemented_as_project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Creator
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    # Metadata
    tags = Column(JSON)
    attachments = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SuiteIntegration(Base):
    """Integration with iTechSmart Suite products"""
    __tablename__ = "suite_integrations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Integration details
    suite_product = Column(String(100), nullable=False)  # enterprise, ninja, qaqc, etc.
    integration_type = Column(String(100))  # api, webhook, direct
    
    # Configuration
    config = Column(JSON)
    credentials = Column(JSON)  # Encrypted
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Indexes for performance
from sqlalchemy import Index

Index('idx_projects_status', Project.status)
Index('idx_projects_creator', Project.creator_id)
Index('idx_messages_project_time', Message.project_id, Message.created_at.desc())
Index('idx_tasks_project_status', Task.project_id, Task.status)
Index('idx_ai_requests_project', AIRequest.project_id)
Index('idx_team_members_project', TeamMember.project_id)