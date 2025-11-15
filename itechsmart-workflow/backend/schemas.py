"""
iTechSmart Workflow - Pydantic Schemas
Request/Response validation schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class WorkflowStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TriggerTypeEnum(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    EVENT = "event"
    API = "api"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []


class WorkflowCreate(WorkflowBase):
    definition: Dict[str, Any] = Field(..., description="Workflow definition with nodes and edges")
    status: Optional[WorkflowStatusEnum] = WorkflowStatusEnum.DRAFT


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    status: Optional[WorkflowStatusEnum] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class WorkflowResponse(WorkflowBase):
    id: int
    status: WorkflowStatusEnum
    definition: Dict[str, Any]
    version: int
    owner_id: int
    is_template: bool
    execution_count: int
    success_count: int
    failure_count: int
    avg_duration_seconds: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: WorkflowStatusEnum
    category: Optional[str]
    tags: Optional[List[str]]
    execution_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Execution Schemas
class ExecutionCreate(BaseModel):
    workflow_id: int
    trigger_type: TriggerTypeEnum = TriggerTypeEnum.MANUAL
    input_data: Optional[Dict[str, Any]] = {}


class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    status: ExecutionStatusEnum
    trigger_type: TriggerTypeEnum
    triggered_by_user_id: Optional[int]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    id: int
    workflow_id: int
    status: ExecutionStatusEnum
    trigger_type: TriggerTypeEnum
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Task Execution Schemas
class TaskExecutionResponse(BaseModel):
    id: int
    execution_id: int
    task_id: str
    task_name: str
    task_type: str
    status: TaskStatusEnum
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Trigger Schemas
class TriggerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    trigger_type: TriggerTypeEnum
    configuration: Dict[str, Any]


class TriggerCreate(TriggerBase):
    workflow_id: int
    is_active: bool = True


class TriggerUpdate(BaseModel):
    name: Optional[str] = None
    trigger_type: Optional[TriggerTypeEnum] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TriggerResponse(TriggerBase):
    id: int
    workflow_id: int
    is_active: bool
    last_triggered_at: Optional[datetime]
    trigger_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workflow Variable Schemas
class WorkflowVariableBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: str
    is_secret: bool = False
    description: Optional[str] = None


class WorkflowVariableCreate(WorkflowVariableBase):
    workflow_id: int


class WorkflowVariableUpdate(BaseModel):
    value: Optional[str] = None
    is_secret: Optional[bool] = None
    description: Optional[str] = None


class WorkflowVariableResponse(WorkflowVariableBase):
    id: int
    workflow_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Integration Schemas
class IntegrationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    configuration: Dict[str, Any]


class IntegrationCreate(IntegrationBase):
    is_active: bool = True


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IntegrationResponse(IntegrationBase):
    id: int
    is_active: bool
    owner_id: int
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    definition: Dict[str, Any]


class TemplateCreate(TemplateBase):
    icon: Optional[str] = None
    is_featured: bool = False


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    definition: Optional[Dict[str, Any]] = None
    icon: Optional[str] = None
    is_featured: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: int
    icon: Optional[str]
    is_featured: bool
    usage_count: int
    rating: int
    created_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schedule Schemas
class ScheduleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    cron_expression: str = Field(..., min_length=1, max_length=100)
    timezone: str = "UTC"


class ScheduleCreate(ScheduleBase):
    workflow_id: int
    is_active: bool = True


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    id: int
    workflow_id: int
    is_active: bool
    next_run_at: Optional[datetime]
    last_run_at: Optional[datetime]
    run_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Execution Log Schemas
class ExecutionLogResponse(BaseModel):
    id: int
    execution_id: int
    level: str
    message: str
    task_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class WorkflowAnalytics(BaseModel):
    total_workflows: int
    active_workflows: int
    draft_workflows: int
    paused_workflows: int
    archived_workflows: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time: float


class ExecutionAnalytics(BaseModel):
    date: str
    total: int
    successful: int
    failed: int
    avg_duration: float


class TopWorkflow(BaseModel):
    workflow_id: int
    workflow_name: str
    execution_count: int
    success_rate: float


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None