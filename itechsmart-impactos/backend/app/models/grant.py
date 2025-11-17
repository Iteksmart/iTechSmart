"""
Grant and Grant Proposal models
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    JSON,
    Boolean,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.models.user import Base
import enum


class GrantStatus(enum.Enum):
    """Grant status enumeration"""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    AWARDED = "awarded"
    COMPLETED = "completed"


class GrantType(enum.Enum):
    """Grant type enumeration"""

    RESEARCH = "research"
    DEVELOPMENT = "development"
    INFRASTRUCTURE = "infrastructure"
    EDUCATION = "education"
    OUTREACH = "outreach"


class Grant(Base):
    """Grant model"""

    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    grant_type = Column(SQLEnum(GrantType), nullable=False)
    status = Column(SQLEnum(GrantStatus), default=GrantStatus.DRAFT)

    # Financial information
    total_amount = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")

    # Dates
    submission_deadline = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    proposals = relationship("GrantProposal", back_populates="grant")

    def __repr__(self):
        return (
            f"<Grant(id={self.id}, title='{self.title}', status='{self.status.value}')>"
        )


class GrantProposal(Base):
    """Grant proposal model"""

    __tablename__ = "grant_proposals"

    id = Column(Integer, primary_key=True, index=True)
    grant_id = Column(Integer, ForeignKey("grants.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Proposal details
    title = Column(String(500), nullable=False)
    abstract = Column(Text, nullable=False)
    narrative = Column(Text, nullable=False)

    # Budget information
    requested_amount = Column(Float, default=0.0)
    budget_justification = Column(Text)

    # Status
    status = Column(SQLEnum(GrantStatus), default=GrantStatus.DRAFT)
    submitted_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional data
    additional_data = Column(JSON)

    # Relationships
    grant = relationship("Grant", back_populates="proposals")
    creator = relationship("User", back_populates="grant_proposals")

    def __repr__(self):
        return f"<GrantProposal(id={self.id}, title='{self.title}', status='{self.status.value}')>"
