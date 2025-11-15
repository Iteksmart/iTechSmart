"""
User schemas for API validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from ..models.user import UserRole, SubscriptionStatus


# User registration
class UserRegister(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    master_password: str = Field(..., min_length=12, max_length=100)
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    @validator("master_password")
    def validate_master_password(cls, v):
        if len(v) < 12:
            raise ValueError("Master password must be at least 12 characters")
        return v


# User login
class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str
    totp_code: Optional[str] = None


# Token response
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# User response
class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    subscription_status: SubscriptionStatus
    subscription_expires_at: Optional[datetime]
    is_verified: bool
    totp_enabled: bool
    biometric_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# User update
class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)
    emergency_contact_email: Optional[EmailStr] = None
    emergency_access_delay_hours: Optional[int] = Field(None, ge=1, le=168)


# Password change
class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# Master password change
class MasterPasswordChange(BaseModel):
    """Master password change schema."""
    current_master_password: str
    new_master_password: str = Field(..., min_length=12, max_length=100)
    
    @validator("new_master_password")
    def validate_new_master_password(cls, v):
        if len(v) < 12:
            raise ValueError("Master password must be at least 12 characters")
        return v


# 2FA setup
class TOTPSetup(BaseModel):
    """TOTP setup response."""
    secret: str
    qr_code_uri: str


class TOTPVerify(BaseModel):
    """TOTP verification schema."""
    code: str = Field(..., min_length=6, max_length=6)


# API key
class APIKeyCreate(BaseModel):
    """API key creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response schema."""
    id: int
    name: str
    key: str  # Only returned on creation
    key_prefix: str
    scopes: list[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyList(BaseModel):
    """API key list item schema."""
    id: int
    name: str
    key_prefix: str
    scopes: list[str]
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Session
class SessionResponse(BaseModel):
    """Session response schema."""
    id: int
    device_name: Optional[str]
    device_type: Optional[str]
    ip_address: Optional[str]
    is_active: bool
    created_at: datetime
    last_used_at: datetime
    
    class Config:
        from_attributes = True


# User stats
class UserStats(BaseModel):
    """User statistics schema."""
    total_passwords: int
    weak_passwords: int
    compromised_passwords: int
    shared_passwords: int
    folders: int
    last_login: Optional[datetime]
    account_age_days: int
    security_score: int