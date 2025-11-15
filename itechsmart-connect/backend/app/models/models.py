"""
iTechSmart Connect - Database Models
SQLAlchemy ORM Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# ============================================================================
# USER MODELS
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="developer")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    apis = relationship("API", back_populates="owner")
    api_keys = relationship("APIKey", back_populates="user")

# ============================================================================
# API MODELS
# ============================================================================

class API(Base):
    __tablename__ = "apis"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    base_url = Column(String(500), nullable=False)
    version = Column(String(50), default="v1")
    status = Column(String(50), default="active", index=True)
    
    # Configuration
    rate_limit = Column(Integer, default=1000)
    timeout = Column(Integer, default=30)
    retry_count = Column(Integer, default=3)
    
    # Metadata
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="apis")
    endpoints = relationship("APIEndpoint", back_populates="api", cascade="all, delete-orphan")
    versions = relationship("APIVersion", back_populates="api", cascade="all, delete-orphan")

class APIEndpoint(Base):
    __tablename__ = "api_endpoints"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    api_id = Column(String, ForeignKey("apis.id"), nullable=False)
    path = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    description = Column(Text)
    
    # Configuration
    rate_limit = Column(Integer)
    timeout = Column(Integer)
    requires_auth = Column(Boolean, default=True)
    
    # Request/Response
    request_schema = Column(JSON)
    response_schema = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api = relationship("API", back_populates="endpoints")

class APIVersion(Base):
    __tablename__ = "api_versions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    api_id = Column(String, ForeignKey("apis.id"), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    is_default = Column(Boolean, default=False)
    changelog = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    deprecated_at = Column(DateTime)
    
    # Relationships
    api = relationship("API", back_populates="versions")

# ============================================================================
# API KEY MODELS
# ============================================================================

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Configuration
    scopes = Column(JSON, default=list)
    rate_limit = Column(Integer, default=1000)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime)
    last_used = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

# ============================================================================
# REQUEST LOG MODELS
# ============================================================================

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    api_id = Column(String, ForeignKey("apis.id"))
    api_key_id = Column(String, ForeignKey("api_keys.id"))
    
    # Request details
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    query_params = Column(JSON)
    headers = Column(JSON)
    
    # Response details
    status_code = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Float, nullable=False)
    response_size_bytes = Column(Integer)
    
    # Client details
    client_ip = Column(String(50))
    user_agent = Column(Text)
    
    # Error details
    error_message = Column(Text)
    error_type = Column(String(100))
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# ============================================================================
# RATE LIMIT MODELS
# ============================================================================

class RateLimit(Base):
    __tablename__ = "rate_limits"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    api_id = Column(String, ForeignKey("apis.id"))
    endpoint_id = Column(String, ForeignKey("api_endpoints.id"))
    
    # Configuration
    limit = Column(Integer, nullable=False)
    window_seconds = Column(Integer, nullable=False, default=60)
    
    # Scope
    scope = Column(String(50), default="global")  # global, api, endpoint, user
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# WEBHOOK MODELS
# ============================================================================

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    
    # Configuration
    events = Column(JSON, default=list)
    secret = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Retry configuration
    retry_count = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=60)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)

class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    webhook_id = Column(String, ForeignKey("webhooks.id"), nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON)
    
    # Delivery details
    status = Column(String(50), nullable=False)  # pending, success, failed
    status_code = Column(Integer)
    response_body = Column(Text)
    error_message = Column(Text)
    
    # Timing
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)

# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class APIMetric(Base):
    __tablename__ = "api_metrics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    api_id = Column(String, ForeignKey("apis.id"), nullable=False)
    
    # Metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, default=0)
    p95_response_time_ms = Column(Float, default=0)
    p99_response_time_ms = Column(Float, default=0)
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# DOCUMENTATION MODELS
# ============================================================================

class APIDocumentation(Base):
    __tablename__ = "api_documentation"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    api_id = Column(String, ForeignKey("apis.id"), nullable=False)
    
    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text)
    content_type = Column(String(50), default="markdown")
    
    # Organization
    section = Column(String(100))
    order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# AUDIT LOG MODELS
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), index=True)
    resource_id = Column(String)
    
    # Details
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)