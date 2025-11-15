"""
Database models for iTechSmart QA/QC System
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class CheckStatus(str, enum.Enum):
    """Status of a QA check"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    RUNNING = "running"
    ERROR = "error"


class CheckCategory(str, enum.Enum):
    """Category of QA check"""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    API = "api"
    DATABASE = "database"
    INTEGRATION = "integration"
    COMPLIANCE = "compliance"
    TESTING = "testing"


class CheckSeverity(str, enum.Enum):
    """Severity level of check failure"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DocumentationType(str, enum.Enum):
    """Type of documentation"""
    README = "readme"
    API_DOCS = "api_docs"
    USER_GUIDE = "user_guide"
    DEPLOYMENT_GUIDE = "deployment_guide"
    ARCHITECTURE = "architecture"
    CHANGELOG = "changelog"
    CONTRIBUTING = "contributing"
    LICENSE = "license"
    SECURITY = "security"


class DocumentationStatus(str, enum.Enum):
    """Status of documentation"""
    UP_TO_DATE = "up_to_date"
    OUTDATED = "outdated"
    MISSING = "missing"
    INCOMPLETE = "incomplete"
    NEEDS_REVIEW = "needs_review"


class ProductStatus(str, enum.Enum):
    """Overall status of a product"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class Product(Base):
    """Product being monitored"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    version = Column(String(50))
    port = Column(Integer)
    base_url = Column(String(500))
    repository_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Status
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.UNKNOWN)
    is_active = Column(Boolean, default=True)
    last_health_check = Column(DateTime)
    last_qa_scan = Column(DateTime)
    
    # Metrics
    qa_score = Column(Float, default=0.0)
    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    warning_checks = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    qa_checks = relationship("QACheck", back_populates="product", cascade="all, delete-orphan")
    qa_results = relationship("QAResult", back_populates="product", cascade="all, delete-orphan")
    documentation = relationship("Documentation", back_populates="product", cascade="all, delete-orphan")
    health_checks = relationship("HealthCheck", back_populates="product", cascade="all, delete-orphan")


class QACheck(Base):
    """Definition of a QA check"""
    __tablename__ = "qa_checks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Check details
    check_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(CheckCategory), nullable=False)
    severity = Column(SQLEnum(CheckSeverity), default=CheckSeverity.MEDIUM)
    
    # Configuration
    is_enabled = Column(Boolean, default=True)
    can_auto_fix = Column(Boolean, default=False)
    check_interval_minutes = Column(Integer, default=60)
    timeout_seconds = Column(Integer, default=300)
    
    # Thresholds
    pass_threshold = Column(Float)
    warning_threshold = Column(Float)
    
    # Metadata
    tags = Column(JSON)
    config = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(DateTime)
    
    # Relationships
    product = relationship("Product", back_populates="qa_checks")
    results = relationship("QAResult", back_populates="check", cascade="all, delete-orphan")


class QAResult(Base):
    """Result of a QA check execution"""
    __tablename__ = "qa_results"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    check_id = Column(Integer, ForeignKey("qa_checks.id"), nullable=False)
    
    # Result details
    status = Column(SQLEnum(CheckStatus), nullable=False)
    score = Column(Float)
    message = Column(Text)
    details = Column(JSON)
    
    # Execution info
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Auto-fix
    auto_fix_attempted = Column(Boolean, default=False)
    auto_fix_successful = Column(Boolean)
    auto_fix_details = Column(JSON)
    
    # Metadata
    environment = Column(String(50))
    triggered_by = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="qa_results")
    check = relationship("QACheck", back_populates="results")


class Documentation(Base):
    """Documentation tracking for products"""
    __tablename__ = "documentation"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Documentation details
    doc_type = Column(SQLEnum(DocumentationType), nullable=False)
    title = Column(String(200), nullable=False)
    file_path = Column(String(500))
    url = Column(String(500))
    
    # Status
    status = Column(SQLEnum(DocumentationStatus), default=DocumentationStatus.MISSING)
    completeness_score = Column(Float, default=0.0)
    
    # Content metrics
    word_count = Column(Integer)
    section_count = Column(Integer)
    code_example_count = Column(Integer)
    
    # Freshness
    last_updated = Column(DateTime)
    last_reviewed = Column(DateTime)
    days_since_update = Column(Integer)
    is_outdated = Column(Boolean, default=False)
    
    # Auto-generation
    is_auto_generated = Column(Boolean, default=False)
    template_used = Column(String(100))
    generation_date = Column(DateTime)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="documentation")


class HealthCheck(Base):
    """Health check results for products"""
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Health status
    is_healthy = Column(Boolean, nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    
    # Details
    message = Column(Text)
    details = Column(JSON)
    
    # Metrics
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    active_connections = Column(Integer)
    
    # Timestamps
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="health_checks")


class QAScan(Base):
    """Complete QA scan session"""
    __tablename__ = "qa_scans"

    id = Column(Integer, primary_key=True, index=True)
    
    # Scan details
    scan_type = Column(String(50))  # full, incremental, targeted
    triggered_by = Column(String(100))
    
    # Scope
    product_ids = Column(JSON)  # List of product IDs scanned
    check_categories = Column(JSON)  # List of categories scanned
    
    # Results
    total_products = Column(Integer, default=0)
    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    warning_checks = Column(Integer, default=0)
    skipped_checks = Column(Integer, default=0)
    
    # Scores
    overall_score = Column(Float, default=0.0)
    average_product_score = Column(Float, default=0.0)
    
    # Execution
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    status = Column(String(50))  # running, completed, failed, cancelled
    
    # Auto-fix
    auto_fixes_attempted = Column(Integer, default=0)
    auto_fixes_successful = Column(Integer, default=0)
    
    # Metadata
    config = Column(JSON)
    summary = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    """Alerts generated by QA/QC system"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Alert details
    alert_type = Column(String(50))  # qa_failure, health_issue, documentation_outdated, etc.
    severity = Column(SQLEnum(CheckSeverity), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Source
    product_id = Column(Integer, ForeignKey("products.id"))
    check_id = Column(Integer, ForeignKey("qa_checks.id"))
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    
    # Actions
    recommended_actions = Column(JSON)
    auto_fix_available = Column(Boolean, default=False)
    
    # Metadata
    details = Column(JSON)
    tags = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Policy(Base):
    """QA/QC policies and rules"""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Policy details
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    policy_type = Column(String(50))  # qa, documentation, security, performance
    
    # Configuration
    is_enabled = Column(Boolean, default=True)
    is_enforced = Column(Boolean, default=False)
    rules = Column(JSON, nullable=False)
    
    # Scope
    applies_to_products = Column(JSON)  # List of product IDs or "all"
    applies_to_categories = Column(JSON)  # List of check categories
    
    # Thresholds
    min_qa_score = Column(Float)
    max_failed_checks = Column(Integer)
    max_critical_issues = Column(Integer)
    
    # Actions
    on_violation_actions = Column(JSON)
    notification_channels = Column(JSON)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_evaluated = Column(DateTime)


class AuditLog(Base):
    """Audit log for QA/QC system actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)
    action_category = Column(String(50))  # qa_check, auto_fix, policy_change, etc.
    description = Column(Text, nullable=False)
    
    # Actor
    user_id = Column(String(100))
    user_name = Column(String(200))
    is_automated = Column(Boolean, default=False)
    
    # Target
    product_id = Column(Integer, ForeignKey("products.id"))
    check_id = Column(Integer, ForeignKey("qa_checks.id"))
    
    # Result
    status = Column(String(50))  # success, failure, partial
    result = Column(JSON)
    
    # Metadata
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    metadata = Column(JSON)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Indexes for performance
from sqlalchemy import Index

Index('idx_qa_results_product_status', QAResult.product_id, QAResult.status)
Index('idx_qa_results_check_status', QAResult.check_id, QAResult.status)
Index('idx_qa_results_created', QAResult.created_at.desc())
Index('idx_health_checks_product_time', HealthCheck.product_id, HealthCheck.checked_at.desc())
Index('idx_alerts_severity_resolved', Alert.severity, Alert.is_resolved)
Index('idx_audit_logs_action_time', AuditLog.action_type, AuditLog.created_at.desc())