"""
Program and Program Metrics models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.models.user import Base


class Program(Base):
    """Program model"""
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Program details
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Program information
    category = Column(String(100), nullable=True)  # Education, Health, Environment, etc.
    target_population = Column(String(255), nullable=True)
    geographic_area = Column(String(255), nullable=True)
    
    # Goals and objectives
    goals = Column(JSON, nullable=True)  # List of program goals
    objectives = Column(JSON, nullable=True)  # List of measurable objectives
    
    # Timeline
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Budget
    total_budget = Column(Float, default=0.0)
    spent_budget = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="planning")  # planning, active, completed, on_hold
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="programs")
    creator = relationship("User", back_populates="created_programs")
    metrics = relationship("ProgramMetric", back_populates="program", cascade="all, delete-orphan")
    impact_reports = relationship("ImpactReport", back_populates="program")
    
    def __repr__(self):
        return f"<Program {self.name}>"


class ProgramMetric(Base):
    """Program metrics and KPIs"""
    __tablename__ = "program_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    
    # Metric details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # output, outcome, impact
    
    # Measurement
    unit = Column(String(50), nullable=True)  # people, hours, dollars, etc.
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0.0)
    
    # Data collection
    collection_frequency = Column(String(50), nullable=True)  # daily, weekly, monthly, quarterly
    data_source = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_measured_at = Column(DateTime, nullable=True)
    
    # Relationships
    program = relationship("Program", back_populates="metrics")
    
    def __repr__(self):
        return f"<ProgramMetric {self.name} ({self.current_value}/{self.target_value} {self.unit})>"