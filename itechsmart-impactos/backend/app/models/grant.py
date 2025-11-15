"""
Grant and Grant Proposal models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.user import Base
import enum


class GrantStatus(str, enum.Enum):
    """Grant status enumeration"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    AWARDED = "awarded"


class Grant(Base):
    """Grant opportunity model"""
    __tablename__ = "grants"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Grant details
    title = Column(String(500), nullable=False, index=True)
    funder_name = Column(String(255), nullable=False)
    funder_website = Column(String(500), nullable=True)
    
    # Grant information
    description = Column(Text, nullable=True)
    focus_areas = Column(JSON, nullable=True)  # List of focus areas
    eligibility_criteria = Column(JSON, nullable=True)
    
    # Financial details
    min_amount = Column(Float, nullable=True)
    max_amount = Column(Float, nullable=True)
    total_available = Column(Float, nullable=True)
    
    # Timeline
    application_deadline = Column(DateTime, nullable=True)
    award_date = Column(DateTime, nullable=True)
    project_start_date = Column(DateTime, nullable=True)
    project_end_date = Column(DateTime, nullable=True)
    
    # Requirements
    required_documents = Column(JSON, nullable=True)
    application_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="grants")
    proposals = relationship("GrantProposal", back_populates="grant")
    
    def __repr__(self):
        return f"<Grant {self.title} by {self.funder_name}>"


class GrantProposal(Base):
    """Grant proposal model"""
    __tablename__ = "grant_proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    grant_id = Column(Integer, ForeignKey("grants.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Proposal details
    title = Column(String(500), nullable=False)
    
    # Proposal sections
    executive_summary = Column(Text, nullable=True)
    problem_statement = Column(Text, nullable=True)
    goals_objectives = Column(JSON, nullable=True)
    methodology = Column(Text, nullable=True)
    timeline = Column(JSON, nullable=True)
    budget = Column(JSON, nullable=True)
    evaluation_plan = Column(Text, nullable=True)
    sustainability_plan = Column(Text, nullable=True)
    
    # Financial request
    requested_amount = Column(Float, nullable=True)
    matching_funds = Column(Float, default=0.0)
    
    # AI assistance tracking
    ai_generated_sections = Column(JSON, nullable=True)  # Track which sections used AI
    ai_model_used = Column(String(100), nullable=True)
    
    # Status
    status = Column(SQLEnum(GrantStatus), default=GrantStatus.DRAFT)
    
    # Submission
    submitted_at = Column(DateTime, nullable=True)
    submission_confirmation = Column(String(255), nullable=True)
    
    # Review
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    # Award
    awarded_at = Column(DateTime, nullable=True)
    awarded_amount = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grant = relationship("Grant", back_populates="proposals")
    creator = relationship("User", back_populates="created_grants")
    
    def __repr__(self):
        return f"<GrantProposal {self.title} - {self.status}>"