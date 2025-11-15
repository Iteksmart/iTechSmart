"""
iTechSmart Pulse - Database Models
SQLAlchemy ORM Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


# ============================================================================
# USER MANAGEMENT
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    avatar_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    dashboards = relationship("Dashboard", back_populates="owner")
    reports = relationship("Report", back_populates="owner")
    queries = relationship("Query", back_populates="creator")


# ============================================================================
# DASHBOARDS
# ============================================================================

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    layout = Column(JSON)  # Grid layout configuration
    filters = Column(JSON)  # Dashboard-level filters
    refresh_interval = Column(Integer, default=300)  # seconds
    views_count = Column(Integer, default=0)
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="dashboards")
    widgets = relationship("Widget", back_populates="dashboard", cascade="all, delete-orphan")


class Widget(Base):
    __tablename__ = "widgets"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id"), nullable=False)
    type = Column(String(50), nullable=False)  # metric, line_chart, bar_chart, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    query_id = Column(String(36), ForeignKey("queries.id"))
    datasource_id = Column(String(36), ForeignKey("datasources.id"))
    position = Column(JSON)  # {x, y, w, h}
    config = Column(JSON)  # Widget-specific configuration
    refresh_interval = Column(Integer)  # Override dashboard refresh
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")
    query = relationship("Query")
    datasource = relationship("DataSource")


# ============================================================================
# REPORTS
# ============================================================================

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    schedule = Column(JSON)  # {frequency, day, time}
    format = Column(String(20), default="pdf")  # pdf, excel, csv
    recipients = Column(JSON)  # List of email addresses
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="reports")
    sections = relationship("ReportSection", back_populates="report", cascade="all, delete-orphan")
    executions = relationship("ReportExecution", back_populates="report")


class ReportSection(Base):
    __tablename__ = "report_sections"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    visualization_type = Column(String(50))
    query_id = Column(String(36), ForeignKey("queries.id"))
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="sections")
    query = relationship("Query")


class ReportExecution(Base):
    __tablename__ = "report_executions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    file_path = Column(String(500))
    file_size = Column(Integer)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    
    # Relationships
    report = relationship("Report", back_populates="executions")


# ============================================================================
# DATA SOURCES
# ============================================================================

class DataSource(Base):
    __tablename__ = "datasources"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # postgresql, mysql, api, etc.
    host = Column(String(255))
    port = Column(Integer)
    database = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))  # Should be encrypted
    connection_string = Column(Text)
    config = Column(JSON)  # Type-specific configuration
    status = Column(String(20), default="pending")  # pending, connected, error
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    queries = relationship("Query", back_populates="datasource")
    tables = relationship("DataSourceTable", back_populates="datasource", cascade="all, delete-orphan")


class DataSourceTable(Base):
    __tablename__ = "datasource_tables"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    datasource_id = Column(String(36), ForeignKey("datasources.id"), nullable=False)
    name = Column(String(255), nullable=False)
    schema = Column(String(255))
    row_count = Column(Integer)
    columns = Column(JSON)  # List of column definitions
    last_synced = Column(DateTime(timezone=True))
    
    # Relationships
    datasource = relationship("DataSource", back_populates="tables")


# ============================================================================
# QUERIES
# ============================================================================

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    datasource_id = Column(String(36), ForeignKey("datasources.id"), nullable=False)
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    parameters = Column(JSON)  # Query parameters
    cache_ttl = Column(Integer, default=300)  # Cache time-to-live in seconds
    is_public = Column(Boolean, default=False)
    execution_count = Column(Integer, default=0)
    avg_execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    datasource = relationship("DataSource", back_populates="queries")
    creator = relationship("User", back_populates="queries")
    executions = relationship("QueryExecution", back_populates="query")


class QueryExecution(Base):
    __tablename__ = "query_executions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    query_id = Column(String(36), ForeignKey("queries.id"), nullable=False)
    status = Column(String(20), nullable=False)  # running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    execution_time_ms = Column(Integer)
    rows_returned = Column(Integer)
    error_message = Column(Text)
    
    # Relationships
    query = relationship("Query", back_populates="executions")


# ============================================================================
# VISUALIZATIONS
# ============================================================================

class Visualization(Base):
    __tablename__ = "visualizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # line_chart, bar_chart, etc.
    description = Column(Text)
    query_id = Column(String(36), ForeignKey("queries.id"))
    config = Column(JSON)  # Visualization-specific configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    query = relationship("Query")


# ============================================================================
# SCHEDULES
# ============================================================================

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # report, dashboard_refresh, etc.
    target_id = Column(String(36), nullable=False)  # ID of report/dashboard
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly
    time = Column(String(10))  # HH:MM
    day_of_week = Column(Integer)  # 0-6 for weekly
    day_of_month = Column(Integer)  # 1-31 for monthly
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# EXPORTS
# ============================================================================

class Export(Base):
    __tablename__ = "exports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    type = Column(String(50), nullable=False)  # dashboard, report, query
    target_id = Column(String(36), nullable=False)
    format = Column(String(20), nullable=False)  # pdf, excel, csv, png
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    file_path = Column(String(500))
    file_size = Column(Integer)
    download_url = Column(String(500))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


# ============================================================================
# ALERTS
# ============================================================================

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    query_id = Column(String(36), ForeignKey("queries.id"), nullable=False)
    condition = Column(JSON)  # Alert condition configuration
    recipients = Column(JSON)  # List of email addresses
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime(timezone=True))
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    query = relationship("Query")


# ============================================================================
# AUDIT LOGS
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


# ============================================================================
# TAGS
# ============================================================================

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7))  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())