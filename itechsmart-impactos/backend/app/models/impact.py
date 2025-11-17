"""
Impact Report, Evidence, and Impact Score models
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
)
from sqlalchemy.orm import relationship
from app.models.user import Base


class ImpactReport(Base):
    """Impact report model"""

    __tablename__ = "impact_reports"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Report details
    title = Column(String(500), nullable=False)
    report_type = Column(
        String(100), nullable=True
    )  # quarterly, annual, project, custom

    # Report period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # Report content
    executive_summary = Column(Text, nullable=True)

    # Metrics and outcomes
    metrics_summary = Column(JSON, nullable=True)  # Key metrics achieved
    outcomes = Column(JSON, nullable=True)  # List of outcomes
    impact_stories = Column(JSON, nullable=True)  # Success stories

    # Financial summary
    total_budget = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    cost_per_beneficiary = Column(Float, nullable=True)

    # Beneficiary data
    total_beneficiaries = Column(Integer, default=0)
    beneficiary_demographics = Column(JSON, nullable=True)

    # Challenges and learnings
    challenges = Column(JSON, nullable=True)
    lessons_learned = Column(JSON, nullable=True)
    future_plans = Column(Text, nullable=True)

    # AI generation
    ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(100), nullable=True)

    # Visualization
    charts_data = Column(JSON, nullable=True)  # Data for charts/graphs

    # Export
    pdf_url = Column(String(500), nullable=True)

    # Sharing
    is_public = Column(Boolean, default=False)
    share_token = Column(String(100), nullable=True, unique=True)

    # Status
    status = Column(String(50), default="draft")  # draft, published, archived

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="impact_reports")
    program = relationship("Program", back_populates="impact_reports")
    creator = relationship("User", back_populates="created_reports")
    evidence = relationship("Evidence", back_populates="impact_report")

    def __repr__(self):
        return f"<ImpactReport {self.title}>"


class Evidence(Base):
    """Evidence and documentation model"""

    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    impact_report_id = Column(Integer, ForeignKey("impact_reports.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)

    # Evidence details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    evidence_type = Column(
        String(100), nullable=True
    )  # photo, video, document, testimonial, data

    # File information
    file_url = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)

    # Metadata
    source = Column(String(255), nullable=True)
    date_collected = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Tags and categorization
    tags = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    impact_report = relationship("ImpactReport", back_populates="evidence")

    def __repr__(self):
        return f"<Evidence {self.title} ({self.evidence_type})>"


class ImpactScore(Base):
    """Impact scoring and assessment model"""

    __tablename__ = "impact_scores"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)

    # Scoring period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Overall score (0-100)
    overall_score = Column(Float, nullable=False)

    # Component scores
    reach_score = Column(Float, nullable=True)  # How many people reached
    depth_score = Column(Float, nullable=True)  # How deeply impacted
    efficiency_score = Column(Float, nullable=True)  # Cost-effectiveness
    sustainability_score = Column(Float, nullable=True)  # Long-term viability
    innovation_score = Column(Float, nullable=True)  # Innovative approaches

    # Detailed breakdown
    score_breakdown = Column(JSON, nullable=True)

    # Benchmarking
    sector_average = Column(Float, nullable=True)
    percentile_rank = Column(Float, nullable=True)

    # AI analysis
    ai_insights = Column(JSON, nullable=True)
    improvement_recommendations = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ImpactScore {self.overall_score}/100>"
