"""
iTechSmart Vault - Pydantic Schemas
Request/Response validation schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class SecretTypeEnum(str, Enum):
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    GENERIC = "generic"


class SecretStatusEnum(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ARCHIVED = "archived"


class PolicyEffectEnum(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class AuditActionEnum(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ROTATE = "rotate"
    SHARE = "share"
    REVOKE = "revoke"


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
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Vault Schemas
class VaultBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = []


class VaultCreate(VaultBase):
    is_default: bool = False


class VaultUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class VaultResponse(VaultBase):
    id: int
    owner_id: int
    is_default: bool
    secret_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Secret Schemas
class SecretBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    secret_type: SecretTypeEnum
    tags: Optional[List[str]] = []


class SecretCreate(SecretBase):
    vault_id: int
    value: str = Field(..., min_length=1)
    expires_at: Optional[datetime] = None
    rotation_interval_days: Optional[int] = None


class SecretUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    tags: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    rotation_interval_days: Optional[int] = None


class SecretResponse(SecretBase):
    id: int
    vault_id: int
    status: SecretStatusEnum
    version: int
    created_by_id: int
    expires_at: Optional[datetime]
    last_rotated_at: Optional[datetime]
    rotation_interval_days: Optional[int]
    access_count: int
    last_accessed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SecretWithValue(SecretResponse):
    """Secret response with decrypted value"""

    value: str


class SecretListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    secret_type: SecretTypeEnum
    status: SecretStatusEnum
    vault_id: int
    access_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Secret Version Schemas
class SecretVersionResponse(BaseModel):
    id: int
    secret_id: int
    version_number: int
    created_by_id: int
    change_description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Policy Schemas
class PolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    effect: PolicyEffectEnum
    actions: List[str]
    resources: List[str]


class PolicyCreate(PolicyBase):
    vault_id: int
    conditions: Optional[Dict[str, Any]] = None
    priority: int = 0


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    effect: Optional[PolicyEffectEnum] = None
    actions: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class PolicyResponse(PolicyBase):
    id: int
    vault_id: int
    conditions: Optional[Dict[str, Any]]
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Access Grant Schemas
class AccessGrantBase(BaseModel):
    secret_id: int
    user_id: int
    permissions: List[str]


class AccessGrantCreate(AccessGrantBase):
    expires_at: Optional[datetime] = None


class AccessGrantUpdate(BaseModel):
    permissions: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class AccessGrantResponse(AccessGrantBase):
    id: int
    granted_by_id: int
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: AuditActionEnum
    resource_type: str
    resource_id: Optional[int]
    resource_name: Optional[str]
    vault_id: Optional[int]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    success: bool
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Secret Rotation Schemas
class SecretRotationRequest(BaseModel):
    rotation_reason: Optional[str] = None


class SecretRotationResponse(BaseModel):
    id: int
    secret_id: int
    old_version: int
    new_version: int
    rotation_type: str
    rotated_by_id: Optional[int]
    rotation_reason: Optional[str]
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Secret Share Schemas
class SecretShareCreate(BaseModel):
    secret_id: int
    max_access_count: int = 1
    expires_in_hours: int = Field(24, ge=1, le=168)  # 1 hour to 7 days


class SecretShareResponse(BaseModel):
    id: int
    secret_id: int
    share_token: str
    shared_by_id: int
    max_access_count: int
    access_count: int
    expires_at: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# API Key Schemas
class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: Optional[List[str]] = []
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: int
    user_id: int
    name: str
    key_prefix: str
    scopes: Optional[List[str]]
    expires_at: Optional[datetime]
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyWithValue(APIKeyResponse):
    """API key response with full key value (only returned on creation)"""

    api_key: str


# Analytics Schemas
class VaultAnalytics(BaseModel):
    total_vaults: int
    total_secrets: int
    active_secrets: int
    expired_secrets: int
    revoked_secrets: int
    total_access_grants: int
    total_policies: int
    secrets_by_type: Dict[str, int]


class SecretAccessStats(BaseModel):
    secret_id: int
    secret_name: str
    access_count: int
    last_accessed_at: Optional[datetime]


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
