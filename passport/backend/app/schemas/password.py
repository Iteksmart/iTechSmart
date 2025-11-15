"""
Password schemas for API validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from ..models.password import PasswordType, PasswordStrength


# Password creation
class PasswordCreate(BaseModel):
    """Password creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    type: PasswordType = PasswordType.LOGIN
    folder: Optional[str] = Field(None, max_length=255)
    
    # Login credentials
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    
    # Card details
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    
    # Metadata
    tags: list[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Auto-rotation
    auto_rotate: bool = False
    rotation_days: Optional[int] = Field(None, ge=1, le=365)


# Password update
class PasswordUpdate(BaseModel):
    """Password update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    folder: Optional[str] = Field(None, max_length=255)
    
    # Login credentials
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    
    # Card details
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    
    # Metadata
    tags: Optional[list[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    # Auto-rotation
    auto_rotate: Optional[bool] = None
    rotation_days: Optional[int] = Field(None, ge=1, le=365)
    
    # Favorites
    is_favorite: Optional[bool] = None


# Password response
class PasswordResponse(BaseModel):
    """Password response schema."""
    id: int
    name: str
    type: PasswordType
    folder: Optional[str]
    
    # Login credentials (decrypted)
    username: Optional[str]
    password: Optional[str]
    url: Optional[str]
    
    # Card details (decrypted)
    card_number: Optional[str]
    card_holder: Optional[str]
    card_expiry: Optional[str]
    card_cvv: Optional[str]
    
    # Notes (decrypted)
    notes: Optional[str]
    
    # Metadata
    tags: list[str]
    custom_fields: Dict[str, Any]
    
    # Security
    password_strength: Optional[PasswordStrength]
    password_score: Optional[float]
    is_compromised: bool
    breach_count: int
    
    # Auto-rotation
    auto_rotate: bool
    rotation_days: Optional[int]
    last_rotated_at: Optional[datetime]
    next_rotation_at: Optional[datetime]
    
    # Sharing
    is_shared: bool
    
    # Favorites
    is_favorite: bool
    
    # Usage
    last_used_at: Optional[datetime]
    usage_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Password list item (without sensitive data)
class PasswordListItem(BaseModel):
    """Password list item schema."""
    id: int
    name: str
    type: PasswordType
    folder: Optional[str]
    username: Optional[str]
    url: Optional[str]
    password_strength: Optional[PasswordStrength]
    is_compromised: bool
    is_favorite: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Password generation
class PasswordGenerateRequest(BaseModel):
    """Password generation request schema."""
    length: int = Field(16, ge=8, le=128)
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = True


class PasswordGenerateResponse(BaseModel):
    """Password generation response schema."""
    password: str
    strength: str
    score: int


# Password strength analysis
class PasswordStrengthRequest(BaseModel):
    """Password strength analysis request."""
    password: str


class PasswordStrengthResponse(BaseModel):
    """Password strength analysis response."""
    score: int
    strength: str
    color: str
    feedback: list[str]


# Folder
class FolderCreate(BaseModel):
    """Folder creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    parent_id: Optional[int] = None


class FolderUpdate(BaseModel):
    """Folder update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)


class FolderResponse(BaseModel):
    """Folder response schema."""
    id: int
    name: str
    icon: Optional[str]
    color: Optional[str]
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Sharing
class PasswordShareRequest(BaseModel):
    """Password sharing request schema."""
    email: str
    can_view: bool = True
    can_edit: bool = False
    can_share: bool = False


class SharedPasswordResponse(BaseModel):
    """Shared password response schema."""
    id: int
    password_id: int
    password_name: str
    owner_email: str
    shared_with_email: str
    can_view: bool
    can_edit: bool
    can_share: bool
    is_accepted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Emergency access
class EmergencyAccessCreate(BaseModel):
    """Emergency access creation schema."""
    grantee_email: str
    delay_hours: int = Field(48, ge=1, le=168)
    access_level: str = Field("view", pattern="^(view|takeover)$")


class EmergencyAccessResponse(BaseModel):
    """Emergency access response schema."""
    id: int
    grantor_email: str
    grantee_email: str
    delay_hours: int
    access_level: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Breach check
class BreachCheckRequest(BaseModel):
    """Breach check request schema."""
    password: str


class BreachCheckResponse(BaseModel):
    """Breach check response schema."""
    is_compromised: bool
    breach_count: int
    message: str