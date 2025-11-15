"""
Pydantic schemas for User and Organization
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole, OAuthProvider


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        from app.core.security import PasswordValidator
        is_valid, error_msg = PasswordValidator.validate(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        from app.core.security import PasswordValidator
        is_valid, error_msg = PasswordValidator.validate(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    oauth_provider: OAuthProvider
    oauth_id: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user response"""
    pass


# ============= Organization Schemas =============

class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    mission: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    slug: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    mission: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = None
    logo_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    ein: Optional[str] = None
    tax_exempt_status: Optional[str] = None


class OrganizationInDB(OrganizationBase):
    """Schema for organization in database"""
    id: int
    slug: str
    logo_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    ein: Optional[str] = None
    tax_exempt_status: Optional[str] = None
    is_active: bool
    is_verified: bool
    subscription_tier: str
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationResponse(OrganizationInDB):
    """Schema for organization response"""
    member_count: Optional[int] = 0
    program_count: Optional[int] = 0


# ============= User-Organization Schemas =============

class UserOrganizationBase(BaseModel):
    """Base user-organization schema"""
    role: UserRole


class UserOrganizationCreate(UserOrganizationBase):
    """Schema for adding user to organization"""
    user_id: int
    organization_id: int


class UserOrganizationUpdate(BaseModel):
    """Schema for updating user role in organization"""
    role: UserRole


class UserOrganizationInDB(UserOrganizationBase):
    """Schema for user-organization in database"""
    id: int
    user_id: int
    organization_id: int
    is_active: bool
    joined_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserOrganizationResponse(UserOrganizationInDB):
    """Schema for user-organization response"""
    user: Optional[UserResponse] = None
    organization: Optional[OrganizationResponse] = None


# ============= Authentication Schemas =============

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: int  # user_id
    exp: datetime
    iat: datetime
    type: str  # access or refresh


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class OAuthLoginRequest(BaseModel):
    """OAuth login request schema"""
    provider: OAuthProvider
    code: str
    redirect_uri: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str