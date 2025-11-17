from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"


class AppStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class PurchaseStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    avatar_url = Column(String(500))
    bio = Column(Text)
    company = Column(String(255))
    website = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    developer_profile = relationship(
        "DeveloperProfile", back_populates="user", uselist=False
    )
    purchases = relationship("Purchase", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")


class DeveloperProfile(Base):
    __tablename__ = "developer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(255))
    tax_id = Column(String(100))
    address = Column(Text)
    phone = Column(String(50))
    support_email = Column(String(255))
    support_url = Column(String(500))
    total_revenue = Column(Float, default=0.0)
    total_downloads = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    stripe_account_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="developer_profile")
    apps = relationship("App", back_populates="developer")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(100))
    parent_id = Column(Integer, ForeignKey("categories.id"))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    apps = relationship("App", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="subcategories")


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    tagline = Column(String(500))
    description = Column(Text, nullable=False)
    long_description = Column(Text)
    icon_url = Column(String(500))
    banner_url = Column(String(500))
    screenshots = Column(JSON)  # Array of screenshot URLs
    video_url = Column(String(500))
    price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=True)
    status = Column(Enum(AppStatus), default=AppStatus.DRAFT, nullable=False)
    version = Column(String(50), default="1.0.0")
    size_mb = Column(Float)
    min_requirements = Column(JSON)
    features = Column(JSON)  # Array of feature strings
    tags = Column(JSON)  # Array of tag strings
    total_downloads = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    featured_order = Column(Integer)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    developer = relationship("DeveloperProfile", back_populates="apps")
    category = relationship("Category", back_populates="apps")
    versions = relationship("AppVersion", back_populates="app")
    reviews = relationship("Review", back_populates="app")
    purchases = relationship("Purchase", back_populates="app")


class AppVersion(Base):
    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    version = Column(String(50), nullable=False)
    release_notes = Column(Text)
    download_url = Column(String(500))
    size_mb = Column(Float)
    min_requirements = Column(JSON)
    is_current = Column(Boolean, default=False)
    downloads = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    app = relationship("App", back_populates="versions")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(255))
    comment = Column(Text)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False)
    is_verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    app = relationship("App", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    responses = relationship("ReviewResponse", back_populates="review")


class ReviewResponse(Base):
    __tablename__ = "review_responses"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="responses")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    transaction_id = Column(String(255), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(
        Enum(PurchaseStatus), default=PurchaseStatus.PENDING, nullable=False
    )
    payment_method = Column(String(50))
    stripe_payment_intent_id = Column(String(255))
    refund_amount = Column(Float)
    refund_reason = Column(Text)
    refunded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="purchases")
    app = relationship("App", back_populates="purchases")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False)
    type = Column(String(50))  # card, bank_account, etc.
    last4 = Column(String(4))
    brand = Column(String(50))
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payment_methods")


class AppAnalytics(Base):
    __tablename__ = "app_analytics"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    unique_visitors = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Wishlist(Base):
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppReport(Base):
    __tablename__ = "app_reports"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
