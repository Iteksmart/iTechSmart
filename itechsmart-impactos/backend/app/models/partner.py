"""
Partner and Partnership models
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.models.user import Base
import enum


class PartnerType(str, enum.Enum):
    """Partner type enumeration"""

    NONPROFIT = "nonprofit"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    FOUNDATION = "foundation"
    ACADEMIC = "academic"
    INDIVIDUAL = "individual"


class PartnershipStatus(str, enum.Enum):
    """Partnership status enumeration"""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    TERMINATED = "terminated"


class Partner(Base):
    """Partner organization/individual model"""

    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)

    # Partner details
    name = Column(String(255), nullable=False, index=True)
    partner_type = Column(SQLEnum(PartnerType), nullable=False)

    # Contact information
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(500), nullable=True)

    # Address
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    # Profile
    description = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    focus_areas = Column(JSON, nullable=True)

    # Capabilities
    resources_offered = Column(
        JSON, nullable=True
    )  # funding, volunteers, expertise, etc.
    expertise_areas = Column(JSON, nullable=True)

    # Social media
    linkedin_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    facebook_url = Column(String(500), nullable=True)

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    partnerships = relationship("Partnership", back_populates="partner")

    def __repr__(self):
        return f"<Partner {self.name} ({self.partner_type})>"


class Partnership(Base):
    """Partnership between organization and partner"""

    __tablename__ = "partnerships"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)

    # Partnership details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    partnership_type = Column(
        String(100), nullable=True
    )  # funding, volunteer, technical, etc.

    # Objectives
    objectives = Column(JSON, nullable=True)
    expected_outcomes = Column(JSON, nullable=True)

    # Timeline
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # Resources
    financial_contribution = Column(Float, default=0.0)
    in_kind_contribution = Column(Text, nullable=True)

    # Agreement
    agreement_url = Column(String(500), nullable=True)
    terms_conditions = Column(Text, nullable=True)

    # Status
    status = Column(SQLEnum(PartnershipStatus), default=PartnershipStatus.PENDING)

    # Progress tracking
    milestones = Column(JSON, nullable=True)
    progress_notes = Column(JSON, nullable=True)

    # Communication
    primary_contact_name = Column(String(255), nullable=True)
    primary_contact_email = Column(String(255), nullable=True)
    primary_contact_phone = Column(String(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="partnerships")
    partner = relationship("Partner", back_populates="partnerships")

    def __repr__(self):
        return f"<Partnership {self.title} - {self.status}>"
