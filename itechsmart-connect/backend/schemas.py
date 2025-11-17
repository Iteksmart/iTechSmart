"""
iTechSmart Connect - Pydantic Schemas
Request/Response validation schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

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
    role: Optional[str] = None


class UserResponse(UserBase):
    id: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API SCHEMAS
# ============================================================================


class APIBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_url: str
    version: str = "v1"


class APICreate(APIBase):
    slug: Optional[str] = None
    rate_limit: int = 1000
    timeout: int = 30


class APIUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None


class APIResponse(APIBase):
    id: str
    slug: str
    status: str
    rate_limit: int
    timeout: int
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API ENDPOINT SCHEMAS
# ============================================================================


class APIEndpointBase(BaseModel):
    path: str
    method: str
    description: Optional[str] = None


class APIEndpointCreate(APIEndpointBase):
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    requires_auth: bool = True
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None


class APIEndpointUpdate(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    requires_auth: Optional[bool] = None


class APIEndpointResponse(APIEndpointBase):
    id: str
    api_id: str
    rate_limit: Optional[int]
    timeout: Optional[int]
    requires_auth: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API VERSION SCHEMAS
# ============================================================================


class APIVersionBase(BaseModel):
    version: str
    changelog: Optional[str] = None


class APIVersionCreate(APIVersionBase):
    is_default: bool = False


class APIVersionResponse(APIVersionBase):
    id: str
    api_id: str
    status: str
    is_default: bool
    created_at: datetime
    deprecated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# API KEY SCHEMAS
# ============================================================================


class APIKeyBase(BaseModel):
    name: str
    scopes: List[str] = []


class APIKeyCreate(APIKeyBase):
    rate_limit: int = 1000
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # Only shown on creation
    scopes: List[str]
    rate_limit: int
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    id: str
    name: str
    key_preview: str  # Masked key
    scopes: List[str]
    is_active: bool
    last_used: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# REQUEST LOG SCHEMAS
# ============================================================================


class RequestLogResponse(BaseModel):
    id: str
    api_id: Optional[str]
    method: str
    path: str
    status_code: int
    response_time_ms: float
    client_ip: Optional[str]
    timestamp: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# RATE LIMIT SCHEMAS
# ============================================================================


class RateLimitBase(BaseModel):
    limit: int
    window_seconds: int = 60


class RateLimitCreate(RateLimitBase):
    api_id: Optional[str] = None
    endpoint_id: Optional[str] = None
    scope: str = "global"


class RateLimitResponse(RateLimitBase):
    id: str
    api_id: Optional[str]
    endpoint_id: Optional[str]
    scope: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# WEBHOOK SCHEMAS
# ============================================================================


class WebhookBase(BaseModel):
    name: str
    url: str
    events: List[str]


class WebhookCreate(WebhookBase):
    secret: Optional[str] = None
    retry_count: int = 3
    retry_delay_seconds: int = 60


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    last_triggered: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================


class AnalyticsOverview(BaseModel):
    total_apis: int
    total_api_keys: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time_ms: float
    timestamp: datetime


class RequestAnalytics(BaseModel):
    period_hours: int
    total_requests: int
    hourly_stats: Dict[str, Dict[str, Any]]


class TopAPI(BaseModel):
    api_id: str
    name: str
    request_count: int


class APIMetricsResponse(BaseModel):
    api_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    period_start: datetime
    period_end: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENTATION SCHEMAS
# ============================================================================


class APIDocumentationBase(BaseModel):
    title: str
    content: str
    content_type: str = "markdown"


class APIDocumentationCreate(APIDocumentationBase):
    section: Optional[str] = None
    order: int = 0


class APIDocumentationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    section: Optional[str] = None
    order: Optional[int] = None


class APIDocumentationResponse(APIDocumentationBase):
    id: str
    api_id: str
    section: Optional[str]
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================


class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    skip: int
    limit: int


# ============================================================================
# ERROR SCHEMAS
# ============================================================================


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
