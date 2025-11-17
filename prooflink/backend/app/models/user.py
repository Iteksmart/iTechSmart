"""
User and Organization models
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Enum as SQLEnum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles"""

    FREE = "free"
    PREMIUM = "premium"
    LIFETIME = "lifetime"
    ORGANIZATION = "organization"
    ADMIN = "admin"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    # Profile
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    website = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Subscription
    role = Column(SQLEnum(UserRole), default=UserRole.FREE)
    subscription_status = Column(
        SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE
    )
    subscription_id = Column(String, nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)

    # Usage tracking
    proofs_created_this_month = Column(Integer, default=0)
    api_calls_today = Column(Integer, default=0)
    storage_used_mb = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    proofs = relationship("Proof", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    integrations = relationship(
        "Integration", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class APIKey(Base):
    """API Key model"""

    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False, index=True)
    key_prefix = Column(String, nullable=False)  # First 8 chars for display

    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_day = Column(Integer, default=1000)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey {self.key_prefix}...>"


class Integration(Base):
    """Third-party integration model"""

    __tablename__ = "integrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    provider = Column(String, nullable=False)  # google_drive, dropbox, slack, etc.
    provider_user_id = Column(String, nullable=True)

    access_token = Column(Text, nullable=True)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)

    # Metadata
    metadata = Column(Text, nullable=True)  # JSON

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="integrations")

    def __repr__(self):
        return f"<Integration {self.provider} for user {self.user_id}>"
