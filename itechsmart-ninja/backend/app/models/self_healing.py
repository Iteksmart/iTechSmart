"""
Database models for self-healing system
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ErrorLog(Base):
    """Log of detected errors"""
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_type = Column(String(100), index=True)
    error_message = Column(Text)
    stack_trace = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    resolved = Column(Boolean, default=False)
    resolution_time = Column(DateTime, nullable=True)
    
    # Relationships
    fixes = relationship("CodeFix", back_populates="error_log")


class CodeFix(Base):
    """Record of code fixes applied"""
    __tablename__ = "code_fixes"
    
    id = Column(Integer, primary_key=True, index=True)
    error_log_id = Column(Integer, ForeignKey("error_logs.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    fix_type = Column(String(50))  # code_change, dependency_update, config_change
    fix_description = Column(Text)
    code_changes = Column(JSON)  # List of changes made
    confidence_score = Column(Float)  # AI confidence in fix
    applied = Column(Boolean, default=False)
    success = Column(Boolean, nullable=True)
    verification_result = Column(JSON, nullable=True)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rollback_available = Column(Boolean, default=True)
    backup_id = Column(String(100), nullable=True)
    
    # Relationships
    error_log = relationship("ErrorLog", back_populates="fixes")


class HealthCheck(Base):
    """System health check results"""
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(JSON)  # Detailed health status
    overall_health = Column(Float)  # 0.0 to 1.0
    issues_detected = Column(Integer, default=0)
    auto_fixed = Column(Integer, default=0)
    manual_review_required = Column(Integer, default=0)


class SystemMetric(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String(50), index=True)  # cpu, memory, disk, network, api_latency
    metric_value = Column(Float)
    unit = Column(String(20))
    threshold_exceeded = Column(Boolean, default=False)
    threshold_value = Column(Float, nullable=True)


class ImprovementSuggestion(Base):
    """AI-generated improvement suggestions"""
    __tablename__ = "improvement_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50))  # performance, security, code_quality, architecture
    title = Column(String(200))
    description = Column(Text)
    impact = Column(String(20))  # low, medium, high
    effort = Column(String(20))  # low, medium, high
    risk = Column(String(20))  # low, medium, high
    confidence = Column(Float)
    implementation_plan = Column(JSON)
    status = Column(String(20), default="pending")  # pending, approved, implemented, rejected
    implemented_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)


class LearningData(Base):
    """Machine learning data from fixes"""
    __tablename__ = "learning_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    error_pattern = Column(Text)
    fix_pattern = Column(Text)
    success_rate = Column(Float)
    times_applied = Column(Integer, default=1)
    avg_confidence = Column(Float)
    context_data = Column(JSON)  # Additional context for ML


class AutoUpdateLog(Base):
    """Log of automatic updates"""
    __tablename__ = "auto_update_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    update_type = Column(String(50))  # dependency, security_patch, feature, optimization
    description = Column(Text)
    changes = Column(JSON)
    version_before = Column(String(20))
    version_after = Column(String(20))
    success = Column(Boolean)
    rollback_available = Column(Boolean, default=True)
    backup_id = Column(String(100), nullable=True)


class InnovationLog(Base):
    """Log of self-generated innovations"""
    __tablename__ = "innovation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    innovation_type = Column(String(50))  # new_feature, optimization, architecture_improvement
    title = Column(String(200))
    description = Column(Text)
    rationale = Column(Text)  # Why this innovation was generated
    implementation = Column(JSON)
    estimated_value = Column(String(100))  # Business value estimate
    status = Column(String(20), default="proposed")  # proposed, approved, implemented
    implemented_at = Column(DateTime, nullable=True)
    impact_metrics = Column(JSON, nullable=True)