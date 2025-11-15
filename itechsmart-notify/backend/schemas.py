"""
iTechSmart Notify - Pydantic Schemas
Request/Response validation schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class NotificationStatusEnum(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ChannelTypeEnum(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationBase(BaseModel):
    channel_type: ChannelTypeEnum
    recipient: str
    recipient_name: Optional[str] = None
    subject: Optional[str] = None
    body: str
    html_body: Optional[str] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.NORMAL


class NotificationCreate(NotificationBase):
    template_id: Optional[int] = None
    template_variables: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatusEnum
    template_id: Optional[int]
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    retry_count: int
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: ChannelTypeEnum
    subject: Optional[str] = None
    body: str
    html_body: Optional[str] = None
    variables: Optional[List[str]] = []


class TemplateCreate(TemplateBase):
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class TemplateResponse(TemplateBase):
    id: int
    is_active: bool
    usage_count: int
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Channel Schemas
class ChannelBase(BaseModel):
    name: str
    channel_type: ChannelTypeEnum
    description: Optional[str] = None
    configuration: Dict[str, Any]


class ChannelCreate(ChannelBase):
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None


class ChannelResponse(ChannelBase):
    id: int
    is_active: bool
    total_sent: int
    total_delivered: int
    total_failed: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class NotificationAnalytics(BaseModel):
    total_notifications: int
    sent_notifications: int
    delivered_notifications: int
    failed_notifications: int
    pending_notifications: int
    delivery_rate: float
    notifications_by_channel: Dict[str, int]


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"