"""
Password and vault models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base
from .user import User


class PasswordType(str, enum.Enum):
    """Password types."""

    LOGIN = "login"
    CARD = "card"
    NOTE = "note"
    IDENTITY = "identity"
    WIFI = "wifi"
    SERVER = "server"
    DATABASE = "database"
    API_KEY = "api_key"


class PasswordStrength(str, enum.Enum):
    """Password strength levels."""

    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"


class Password(Base):
    """Password/credential model."""

    __tablename__ = "passwords"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[PasswordType] = mapped_column(
        SQLEnum(PasswordType), default=PasswordType.LOGIN
    )
    folder: Mapped[Optional[str]] = mapped_column(String(255))

    # Login credentials (encrypted)
    username: Mapped[Optional[str]] = mapped_column(Text)
    encrypted_password: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)

    # Card details (encrypted)
    card_number: Mapped[Optional[str]] = mapped_column(Text)
    card_holder: Mapped[Optional[str]] = mapped_column(Text)
    card_expiry: Mapped[Optional[str]] = mapped_column(String(10))
    card_cvv: Mapped[Optional[str]] = mapped_column(Text)

    # Notes (encrypted)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    tags: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    custom_fields: Mapped[Optional[str]] = mapped_column(Text)  # JSON object

    # Security
    password_strength: Mapped[Optional[PasswordStrength]] = mapped_column(
        SQLEnum(PasswordStrength)
    )
    password_score: Mapped[Optional[float]] = mapped_column(Float)
    is_compromised: Mapped[bool] = mapped_column(Boolean, default=False)
    breach_count: Mapped[int] = mapped_column(Integer, default=0)

    # Auto-rotation
    auto_rotate: Mapped[bool] = mapped_column(Boolean, default=False)
    rotation_days: Mapped[Optional[int]] = mapped_column(Integer)
    last_rotated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_rotation_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Sharing
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    shared_with: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of user IDs

    # Favorites
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Usage tracking
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="passwords")
    history: Mapped[List["PasswordHistory"]] = relationship(
        "PasswordHistory", back_populates="password", cascade="all, delete-orphan"
    )


class PasswordHistory(Base):
    """Password history model."""

    __tablename__ = "password_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    password_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Historical data
    encrypted_password: Mapped[str] = mapped_column(Text, nullable=False)
    password_strength: Mapped[Optional[PasswordStrength]] = mapped_column(
        SQLEnum(PasswordStrength)
    )
    password_score: Mapped[Optional[float]] = mapped_column(Float)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    password: Mapped["Password"] = relationship("Password", back_populates="history")


class Folder(Base):
    """Folder model for organizing passwords."""

    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Folder info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(20))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer)

    # Status
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SharedPassword(Base):
    """Shared password model."""

    __tablename__ = "shared_passwords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    password_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    shared_with_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Permissions
    can_view: Mapped[bool] = mapped_column(Boolean, default=True)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)
    can_share: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class EmergencyAccess(Base):
    """Emergency access model."""

    __tablename__ = "emergency_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grantor_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    grantee_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Settings
    delay_hours: Mapped[int] = mapped_column(Integer, default=48)
    access_level: Mapped[str] = mapped_column(
        String(50), default="view"
    )  # view, takeover

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, active, requested, granted, rejected

    # Request tracking
    requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
