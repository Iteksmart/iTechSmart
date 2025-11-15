"""
iTechSmart Forge - Database Models
Low-Code/No-Code Application Builder with AI
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AppStatus(str, Enum):
    """Application status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ComponentType(str, Enum):
    """UI component types"""
    BUTTON = "button"
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TABLE = "table"
    CHART = "chart"
    FORM = "form"
    CARD = "card"
    MODAL = "modal"
    TABS = "tabs"
    LIST = "list"
    GRID = "grid"
    IMAGE = "image"
    VIDEO = "video"
    MAP = "map"
    CALENDAR = "calendar"
    FILE_UPLOAD = "file_upload"
    CUSTOM = "custom"


class DataSourceType(str, Enum):
    """Data source types"""
    ITECHSMART_PRODUCT = "itechsmart_product"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class WorkflowTriggerType(str, Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    DATA_CHANGE = "data_change"


class DeploymentStatus(str, Enum):
    """Deployment status"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    avatar_url = Column(String(500))
    bio = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    apps = relationship("App", back_populates="owner", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="creator", cascade="all, delete-orphan")


class App(Base):
    """Application model"""
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(500))
    
    # Status
    status = Column(String(20), default=AppStatus.DRAFT.value, index=True)
    version = Column(String(50), default="1.0.0")
    
    # Configuration
    theme = Column(JSON)  # Color scheme, fonts, etc.
    layout = Column(JSON)  # Page layout configuration
    settings = Column(JSON)  # App-specific settings
    
    # Metadata
    tags = Column(JSON)  # List of tags
    category = Column(String(100))
    
    # Analytics
    view_count = Column(Integer, default=0)
    clone_count = Column(Integer, default=0)
    
    # Marketplace
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    price = Column(Float, default=0.0)  # 0 = free
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="apps")
    pages = relationship("Page", back_populates="app", cascade="all, delete-orphan")
    data_sources = relationship("DataSource", back_populates="app", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="app", cascade="all, delete-orphan")
    permissions = relationship("AppPermission", back_populates="app", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="app", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_app_owner_status', 'owner_id', 'status'),
    )


class Page(Base):
    """Page within an app"""
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # Basic info
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    title = Column(String(200))
    description = Column(Text)
    
    # Configuration
    layout = Column(JSON)  # Page layout
    components = Column(JSON)  # List of components on page
    styles = Column(JSON)  # Custom CSS
    scripts = Column(JSON)  # Custom JavaScript
    
    # Navigation
    is_home = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    parent_page_id = Column(Integer, ForeignKey("pages.id"))
    
    # SEO
    meta_title = Column(String(200))
    meta_description = Column(Text)
    meta_keywords = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    app = relationship("App", back_populates="pages")
    parent_page = relationship("Page", remote_side=[id])

    __table_args__ = (
        Index('idx_page_app_slug', 'app_id', 'slug'),
    )


class Component(Base):
    """Reusable UI component"""
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(200), nullable=False, index=True)
    component_type = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(500))
    
    # Configuration
    props = Column(JSON)  # Component properties
    default_props = Column(JSON)  # Default property values
    styles = Column(JSON)  # Default styles
    
    # Code
    template = Column(Text)  # HTML template
    script = Column(Text)  # JavaScript code
    
    # Metadata
    category = Column(String(100))
    tags = Column(JSON)
    
    # Marketplace
    is_public = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    price = Column(Float, default=0.0)
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataSource(Base):
    """Data source connection"""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # Basic info
    name = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    
    # Connection details
    connection_config = Column(JSON)  # Connection parameters (encrypted)
    
    # For iTechSmart products
    product_name = Column(String(100))  # e.g., "itechsmart-analytics"
    
    # For databases
    host = Column(String(255))
    port = Column(Integer)
    database = Column(String(200))
    username = Column(String(200))
    
    # For APIs
    base_url = Column(String(500))
    auth_type = Column(String(50))  # none, basic, bearer, oauth2
    auth_config = Column(JSON)  # Auth credentials (encrypted)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_tested = Column(DateTime)
    test_status = Column(String(50))  # success, failed
    test_message = Column(Text)
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    app = relationship("App", back_populates="data_sources")
    queries = relationship("DataQuery", back_populates="data_source", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_datasource_app_type', 'app_id', 'source_type'),
    )


class DataQuery(Base):
    """Saved data query"""
    __tablename__ = "data_queries"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    
    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Query
    query_type = Column(String(50))  # sql, graphql, rest, etc.
    query = Column(Text, nullable=False)
    parameters = Column(JSON)  # Query parameters
    
    # Caching
    cache_enabled = Column(Boolean, default=False)
    cache_ttl = Column(Integer, default=300)  # seconds
    
    # Transformation
    transform_script = Column(Text)  # JavaScript to transform results
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed = Column(DateTime)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="queries")


class Workflow(Base):
    """Automated workflow"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Trigger
    trigger_type = Column(String(50), nullable=False)
    trigger_config = Column(JSON)  # Trigger configuration
    
    # Steps
    steps = Column(JSON, nullable=False)  # List of workflow steps
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Execution stats
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_execution = Column(DateTime)
    last_status = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    app = relationship("App", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowExecution(Base):
    """Workflow execution history"""
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    
    # Execution details
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    duration_ms = Column(Float)
    
    # Status
    status = Column(String(50), nullable=False)  # running, success, failed
    
    # Results
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Step results
    step_results = Column(JSON)  # Results from each step
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")


class AppPermission(Base):
    """App access permissions"""
    __tablename__ = "app_permissions"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # User or role
    user_id = Column(Integer, ForeignKey("users.id"))
    role_name = Column(String(100))
    
    # Permissions
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    can_deploy = Column(Boolean, default=False)
    
    # Custom permissions
    custom_permissions = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    app = relationship("App", back_populates="permissions")

    __table_args__ = (
        Index('idx_permission_app_user', 'app_id', 'user_id'),
    )


class Template(Base):
    """App template"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    thumbnail = Column(String(500))
    
    # Template data
    template_data = Column(JSON, nullable=False)  # Complete app configuration
    
    # Category
    category = Column(String(100), index=True)
    tags = Column(JSON)
    
    # Marketplace
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    price = Column(Float, default=0.0)
    
    # Stats
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="templates")


class Deployment(Base):
    """App deployment"""
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    
    # Deployment info
    version = Column(String(50), nullable=False)
    environment = Column(String(50), default="production")  # dev, staging, production
    
    # Status
    status = Column(String(50), nullable=False, default=DeploymentStatus.PENDING.value)
    
    # URLs
    deployment_url = Column(String(500))
    preview_url = Column(String(500))
    
    # Configuration
    build_config = Column(JSON)
    environment_vars = Column(JSON)
    
    # Build info
    build_started_at = Column(DateTime)
    build_completed_at = Column(DateTime)
    build_duration_ms = Column(Float)
    build_log = Column(Text)
    
    # Deployment info
    deployed_at = Column(DateTime)
    deployment_log = Column(Text)
    
    # Error info
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    app = relationship("App", back_populates="deployments")

    __table_args__ = (
        Index('idx_deployment_app_status', 'app_id', 'status'),
    )


class AIRequest(Base):
    """AI-powered generation request"""
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request
    request_type = Column(String(50), nullable=False)  # generate_app, generate_component, etc.
    prompt = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context
    
    # Response
    response = Column(JSON)  # Generated content
    
    # Status
    status = Column(String(50), nullable=False)  # pending, processing, completed, failed
    
    # Timing
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    duration_ms = Column(Float)
    
    # Error
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)