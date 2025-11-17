from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"


class AppStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class PurchaseStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Developer Profile Schemas
class DeveloperProfileBase(BaseModel):
    company_name: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    support_email: Optional[EmailStr] = None
    support_url: Optional[str] = None


class DeveloperProfileCreate(DeveloperProfileBase):
    pass


class DeveloperProfileUpdate(DeveloperProfileBase):
    pass


class DeveloperProfileResponse(DeveloperProfileBase):
    id: int
    user_id: int
    total_revenue: float
    total_downloads: int
    average_rating: float
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# App Schemas
class AppBase(BaseModel):
    name: str
    slug: str
    category_id: int
    tagline: Optional[str] = None
    description: str
    long_description: Optional[str] = None
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    screenshots: Optional[List[str]] = []
    video_url: Optional[str] = None
    price: float = 0.0
    is_free: bool = True
    version: str = "1.0.0"
    size_mb: Optional[float] = None
    min_requirements: Optional[dict] = {}
    features: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class AppCreate(AppBase):
    pass


class AppUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    screenshots: Optional[List[str]] = None
    video_url: Optional[str] = None
    price: Optional[float] = None
    is_free: Optional[bool] = None
    version: Optional[str] = None
    size_mb: Optional[float] = None
    min_requirements: Optional[dict] = None
    features: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[AppStatus] = None


class AppResponse(AppBase):
    id: int
    developer_id: int
    status: AppStatus
    total_downloads: int
    total_revenue: float
    average_rating: float
    total_reviews: int
    is_featured: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppDetailResponse(AppResponse):
    developer: DeveloperProfileResponse
    category: CategoryResponse


# App Version Schemas
class AppVersionBase(BaseModel):
    version: str
    release_notes: Optional[str] = None
    download_url: Optional[str] = None
    size_mb: Optional[float] = None
    min_requirements: Optional[dict] = {}


class AppVersionCreate(AppVersionBase):
    app_id: int


class AppVersionResponse(AppVersionBase):
    id: int
    app_id: int
    is_current: bool
    downloads: int
    created_at: datetime

    class Config:
        from_attributes = True


# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    app_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: int
    app_id: int
    user_id: int
    status: ReviewStatus
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewResponseCreate(BaseModel):
    response: str


class ReviewResponseResponse(BaseModel):
    id: int
    review_id: int
    developer_id: int
    response: str
    created_at: datetime

    class Config:
        from_attributes = True


# Purchase Schemas
class PurchaseCreate(BaseModel):
    app_id: int
    payment_method_id: str


class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    app_id: int
    transaction_id: str
    amount: float
    currency: str
    status: PurchaseStatus
    payment_method: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Payment Method Schemas
class PaymentMethodCreate(BaseModel):
    stripe_payment_method_id: str
    type: str
    last4: str
    brand: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False


class PaymentMethodResponse(BaseModel):
    id: int
    user_id: int
    type: str
    last4: str
    brand: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class AppAnalyticsResponse(BaseModel):
    id: int
    app_id: int
    date: datetime
    views: int
    downloads: int
    purchases: int
    revenue: float
    unique_visitors: int
    conversion_rate: float

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_apps: int
    total_downloads: int
    total_revenue: float
    total_users: int
    total_developers: int
    total_reviews: int
    average_rating: float


class DeveloperStats(BaseModel):
    total_apps: int
    total_downloads: int
    total_revenue: float
    average_rating: float
    total_reviews: int
    active_users: int


# Wishlist Schemas
class WishlistCreate(BaseModel):
    app_id: int


class WishlistResponse(BaseModel):
    id: int
    user_id: int
    app_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Report Schemas
class AppReportCreate(BaseModel):
    app_id: int
    reason: str
    description: Optional[str] = None


class AppReportResponse(BaseModel):
    id: int
    app_id: int
    user_id: int
    reason: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Search Schemas
class AppSearchParams(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_free: Optional[bool] = None
    min_rating: Optional[float] = None
    tags: Optional[List[str]] = None
    sort_by: str = "popularity"  # popularity, rating, price, newest
    page: int = 1
    page_size: int = 20


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
