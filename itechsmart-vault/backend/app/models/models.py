"""
iTechSmart Vault - Database Models
Secrets Management Platform
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, LargeBinary, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class SecretType(str, enum.Enum):
    """Secret type enumeration"""
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    GENERIC = "generic"


class SecretStatus(str, enum.Enum):
    """Secret status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ARCHIVED = "archived"


class PolicyEffect(str, enum.Enum):
    """Policy effect enumeration"""
    ALLOW = "allow"
    DENY = "deny"


class AuditAction(str, enum.Enum):
    """Audit action enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ROTATE = "rotate"
    SHARE = "share"
    REVOKE = "revoke"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vaults = relationship("Vault", back_populates="owner", cascade="all, delete-orphan")
    secrets = relationship("Secret", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")
    access_grants = relationship("AccessGrant", back_populates="user")


class Vault(Base):
    """Vault model - container for organizing secrets"""
    __tablename__ = "vaults"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_default = Column(Boolean, default=False)
    encryption_key_id = Column(String(255))  # Reference to encryption key
    tags = Column(JSON)
    metadata = Column(JSON)
    secret_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="vaults")
    secrets = relationship("Secret", back_populates="vault", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="vault", cascade="all, delete-orphan")


class Secret(Base):
    """Secret model - stores encrypted sensitive data"""
    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, index=True)
    vault_id = Column(Integer, ForeignKey("vaults.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    secret_type = Column(SQLEnum(SecretType), nullable=False, index=True)
    status = Column(SQLEnum(SecretStatus), default=SecretStatus.ACTIVE, index=True)
    encrypted_value = Column(LargeBinary, nullable=False)  # Encrypted secret data
    encryption_algorithm = Column(String(50), default="AES-256-GCM")
    version = Column(Integer, default=1)
    current_version_id = Column(Integer, ForeignKey("secret_versions.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tags = Column(JSON)
    metadata = Column(JSON)
    expires_at = Column(DateTime)
    last_rotated_at = Column(DateTime)
    rotation_interval_days = Column(Integer)  # Auto-rotation interval
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vault = relationship("Vault", back_populates="secrets")
    created_by_user = relationship("User", back_populates="secrets")
    versions = relationship("SecretVersion", back_populates="secret", cascade="all, delete-orphan", foreign_keys="SecretVersion.secret_id")
    access_grants = relationship("AccessGrant", back_populates="secret", cascade="all, delete-orphan")


class SecretVersion(Base):
    """Secret version model - maintains version history"""
    __tablename__ = "secret_versions"

    id = Column(Integer, primary_key=True, index=True)
    secret_id = Column(Integer, ForeignKey("secrets.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    encrypted_value = Column(LargeBinary, nullable=False)
    encryption_algorithm = Column(String(50), default="AES-256-GCM")
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_description = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    secret = relationship("Secret", back_populates="versions", foreign_keys=[secret_id])


class Policy(Base):
    """Policy model - defines access control rules"""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    vault_id = Column(Integer, ForeignKey("vaults.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    effect = Column(SQLEnum(PolicyEffect), nullable=False)
    actions = Column(JSON, nullable=False)  # List of allowed/denied actions
    resources = Column(JSON, nullable=False)  # Resource patterns
    conditions = Column(JSON)  # Conditional rules
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vault = relationship("Vault", back_populates="policies")


class AccessGrant(Base):
    """Access grant model - grants user access to secrets"""
    __tablename__ = "access_grants"

    id = Column(Integer, primary_key=True, index=True)
    secret_id = Column(Integer, ForeignKey("secrets.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    granted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permissions = Column(JSON, nullable=False)  # List of permissions (read, write, delete, etc.)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    secret = relationship("Secret", back_populates="access_grants")
    user = relationship("User", back_populates="access_grants")


class AuditLog(Base):
    """Audit log model - tracks all secret operations"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer)
    resource_name = Column(String(255))
    vault_id = Column(Integer, ForeignKey("vaults.id"), index=True)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class EncryptionKey(Base):
    """Encryption key model - manages encryption keys"""
    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    algorithm = Column(String(50), default="AES-256-GCM")
    encrypted_key = Column(LargeBinary, nullable=False)  # Master key encrypted
    key_version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_master = Column(Boolean, default=False)
    rotation_schedule = Column(String(100))  # Cron expression
    last_rotated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SecretRotation(Base):
    """Secret rotation model - tracks rotation history"""
    __tablename__ = "secret_rotations"

    id = Column(Integer, primary_key=True, index=True)
    secret_id = Column(Integer, ForeignKey("secrets.id"), nullable=False, index=True)
    old_version = Column(Integer, nullable=False)
    new_version = Column(Integer, nullable=False)
    rotation_type = Column(String(50))  # manual, automatic, scheduled
    rotated_by_id = Column(Integer, ForeignKey("users.id"))
    rotation_reason = Column(Text)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SecretShare(Base):
    """Secret share model - temporary secret sharing"""
    __tablename__ = "secret_shares"

    id = Column(Integer, primary_key=True, index=True)
    secret_id = Column(Integer, ForeignKey("secrets.id"), nullable=False, index=True)
    share_token = Column(String(255), unique=True, nullable=False, index=True)
    shared_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_access_count = Column(Integer, default=1)
    access_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    secret = relationship("Secret")


class APIKey(Base):
    """API key model - manages API access keys"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)  # First few chars for identification
    scopes = Column(JSON)  # List of allowed scopes
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)