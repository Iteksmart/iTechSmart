"""
iTechSmart Notify - Database Models
Notification Service Platform
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class NotificationStatus(str, enum.Enum):
    """Notification status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriority(str, enum.Enum):
    """Notification priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ChannelType(str, enum.Enum):
    """Channel type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class TemplateType(str, enum.Enum):
    """Template type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notifications = relationship("Notification", back_populates="user")
    templates = relationship("Template", back_populates="created_by_user")
    channels = relationship("Channel", back_populates="owner")


class Notification(Base):
    """Notification model - represents a notification to be sent"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel_type = Column(SQLEnum(ChannelType), nullable=False, index=True)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL, index=True)
    
    # Recipient information
    recipient = Column(String(255), nullable=False)  # Email, phone, device token, etc.
    recipient_name = Column(String(255))
    
    # Content
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    html_body = Column(Text)
    
    # Template
    template_id = Column(Integer, ForeignKey("templates.id"))
    template_variables = Column(JSON)
    
    # Scheduling
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    
    # Metadata
    metadata = Column(JSON)
    tags = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("Template")
    delivery_logs = relationship("DeliveryLog", back_populates="notification", cascade="all, delete-orphan")


class Template(Base):
    """Template model - notification templates"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    template_type = Column(SQLEnum(TemplateType), nullable=False, index=True)
    
    # Template content
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    html_body = Column(Text)
    
    # Variables
    variables = Column(JSON)  # List of variable names
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    category = Column(String(100))
    tags = Column(JSON)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by_user = relationship("User", back_populates="templates")


class Channel(Base):
    """Channel model - notification channel configuration"""
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    channel_type = Column(SQLEnum(ChannelType), nullable=False, index=True)
    description = Column(Text)
    
    # Configuration
    configuration = Column(JSON, nullable=False)  # Channel-specific config
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer)
    rate_limit_per_hour = Column(Integer)
    rate_limit_per_day = Column(Integer)
    
    # Usage tracking
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="channels")


class DeliveryLog(Base):
    """Delivery log model - tracks notification delivery attempts"""
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False, index=True)
    
    # Attempt information
    attempt_number = Column(Integer, nullable=False)
    status = Column(SQLEnum(NotificationStatus), nullable=False)
    
    # Response
    response_code = Column(String(50))
    response_message = Column(Text)
    response_data = Column(JSON)
    
    # Timing
    attempted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)
    
    # Error tracking
    error_message = Column(Text)
    error_code = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    notification = relationship("Notification", back_populates="delivery_logs")


class Schedule(Base):
    """Schedule model - scheduled notification jobs"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Schedule configuration
    cron_expression = Column(String(100))
    timezone = Column(String(50), default="UTC")
    
    # Notification template
    channel_type = Column(SQLEnum(ChannelType), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"))
    
    # Recipients
    recipients = Column(JSON, nullable=False)  # List of recipients
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Tracking
    next_run_at = Column(DateTime)
    last_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscriber(Base):
    """Subscriber model - manages notification subscribers"""
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True)
    phone_number = Column(String(20), index=True)
    device_token = Column(String(500))
    
    # Preferences
    preferences = Column(JSON)  # Channel preferences
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(JSON)
    tags = Column(JSON)
    
    # Tracking
    total_notifications_received = Column(Integer, default=0)
    last_notification_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Webhook(Base):
    """Webhook model - webhook endpoints for callbacks"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    
    # Events to trigger on
    events = Column(JSON, nullable=False)  # List of event types
    
    # Authentication
    secret = Column(String(255))
    headers = Column(JSON)
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Tracking
    total_calls = Column(Integer, default=0)
    last_called_at = Column(DateTime)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit log model - tracks all system operations"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)