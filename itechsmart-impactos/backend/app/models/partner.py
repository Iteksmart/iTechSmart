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
    Float,
    Boolean,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.models.user import Base
import enum


class PartnershipType(enum.Enum):
    """Partnership type enumeration"""

    STRATEGIC = "strategic"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    ACADEMIC = "academic"
    COMMERCIAL = "commercial"


class PartnershipStatus(enum.Enum):
    """Partnership status enumeration"""

    POTENTIAL = "potential"
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


class Partner(Base):
    """Partner model"""

    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Contact information
    website = Column(String(500))
    email = Column(String(200))
    phone = Column(String(50))

    # Address
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))

    # Partner type
    partner_type = Column(String(50))  # Organization type

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    partnerships = relationship("Partnership", back_populates="partner")

    def __repr__(self):
        return f"<Partner(id={self.id}, name='{self.name}', active={self.is_active})>"


class Partnership(Base):
    """Partnership model"""

    __tablename__ = "partnerships"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Partnership details
    partnership_type = Column(SQLEnum(PartnershipType), nullable=False)
    status = Column(SQLEnum(PartnershipStatus), default=PartnershipStatus.POTENTIAL)

    # Financial information
    financial_contribution = Column(Float, default=0.0)
    in_kind_contribution = Column(Text)

    # Dates
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Description and objectives
    description = Column(Text)
    objectives = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional data
    agreement_details = Column(JSON)

    # Relationships
    partner = relationship("Partner", back_populates="partnerships")
    project = relationship("Project", back_populates="partnerships")

    def __repr__(self):
        return f"<Partnership(id={self.id}, type='{self.partnership_type.value}', status='{self.status.value}')>"
