"""
User and Organization models
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    PROGRAM_MANAGER = "program_manager"
    GRANT_WRITER = "grant_writer"
    DATA_ANALYST = "data_analyst"
    VOLUNTEER = "volunteer"
    DONOR = "donor"


class OAuthProvider(str, enum.Enum):
    """OAuth provider enumeration"""
    GOOGLE = "google"
    GITHUB = "github"
    LOCAL = "local"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    
    # OAuth fields
    oauth_provider = Column(SQLEnum(OAuthProvider), default=OAuthProvider.LOCAL)
    oauth_id = Column(String(255), nullable=True, index=True)
    oauth_access_token = Column(String(500), nullable=True)
    oauth_refresh_token = Column(String(500), nullable=True)
    
    # Profile fields
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(String(1000), nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    organizations = relationship("UserOrganization", back_populates="user")
    created_programs = relationship("Program", back_populates="creator")
    created_grants = relationship("GrantProposal", back_populates="creator")
    created_reports = relationship("ImpactReport", back_populates="creator")
    
    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


class Organization(Base):
    """Organization model"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    
    # Organization details
    description = Column(String(2000), nullable=True)
    mission = Column(String(1000), nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    
    # Tax information
    ein = Column(String(20), nullable=True)  # Employer Identification Number
    tax_exempt_status = Column(String(50), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Subscription
    subscription_tier = Column(String(50), default="free")  # free, basic, pro, enterprise
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("UserOrganization", back_populates="organization")
    programs = relationship("Program", back_populates="organization")
    grants = relationship("Grant", back_populates="organization")
    impact_reports = relationship("ImpactReport", back_populates="organization")
    partnerships = relationship("Partnership", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization {self.name}>"


class UserOrganization(Base):
    """User-Organization association with roles"""
    __tablename__ = "user_organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Role in organization
    role = Column(SQLEnum(UserRole), default=UserRole.VOLUNTEER)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="members")
    
    def __repr__(self):
        return f"<UserOrganization user_id={self.user_id} org_id={self.organization_id} role={self.role}>"