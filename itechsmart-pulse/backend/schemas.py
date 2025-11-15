"""
iTechSmart Pulse - Pydantic Schemas
Request/Response Models
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class DashboardStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"

class ReportStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DataSourceType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    API = "api"
    GOOGLE_SHEETS = "google_sheets"
    EXCEL = "excel"
    CSV = "csv"

class VisualizationType(str, Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    TABLE = "table"
    METRIC = "metric"
    GAUGE = "gauge"
    HEATMAP = "heatmap"


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class WidgetPosition(BaseModel):
    x: int
    y: int
    w: int
    h: int

class WidgetBase(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    query_id: Optional[str] = None
    datasource_id: Optional[str] = None
    position: WidgetPosition
    config: Optional[Dict[str, Any]] = None

class WidgetCreate(WidgetBase):
    dashboard_id: str

class WidgetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[WidgetPosition] = None
    config: Optional[Dict[str, Any]] = None

class WidgetResponse(WidgetBase):
    id: str
    dashboard_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    layout: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    refresh_interval: int = 300
    tags: Optional[List[str]] = None

class DashboardCreate(DashboardBase):
    pass

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    layout: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    tags: Optional[List[str]] = None

class DashboardResponse(DashboardBase):
    id: str
    owner_id: str
    views_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    widgets: List[WidgetResponse] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# REPORT SCHEMAS
# ============================================================================

class ReportSchedule(BaseModel):
    frequency: str
    day: Optional[int] = None
    time: str = "00:00"

class ReportSectionBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    visualization_type: Optional[str] = None
    query_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ReportSectionCreate(ReportSectionBase):
    report_id: str

class ReportSectionResponse(ReportSectionBase):
    id: str
    report_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    schedule: Optional[ReportSchedule] = None
    format: ReportFormat = ReportFormat.PDF
    recipients: List[EmailStr] = []
    is_active: bool = True

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    schedule: Optional[ReportSchedule] = None
    format: Optional[ReportFormat] = None
    recipients: Optional[List[EmailStr]] = None
    is_active: Optional[bool] = None

class ReportResponse(ReportBase):
    id: str
    owner_id: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    sections: List[ReportSectionResponse] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# COMMON SCHEMAS
# ============================================================================

class MessageResponse(BaseModel):
    message: str
    id: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str