"""
Database Models for iTechSmart HL7
SQLAlchemy models for all entities
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class MessageStatus(enum.Enum):
    """HL7 message status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class IncidentSeverity(enum.Enum):
    """Incident severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NoteStatus(enum.Enum):
    """Clinical note status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    SIGNED = "signed"
    AMENDED = "amended"
    DELETED = "deleted"


# HL7 Message Model
class HL7Message(Base):
    __tablename__ = 'hl7_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(100), unique=True, index=True)
    message_type = Column(String(50))  # ADT, ORM, ORU, etc.
    message_version = Column(String(10))  # 2.5, 2.6, FHIR, etc.
    
    # Message content
    raw_message = Column(Text)
    parsed_data = Column(JSON)
    
    # Routing information
    sending_application = Column(String(100))
    sending_facility = Column(String(100))
    receiving_application = Column(String(100))
    receiving_facility = Column(String(100))
    
    # Status
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.PENDING)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    incidents = relationship("Incident", back_populates="message")
    
    # Patient reference
    patient_id = Column(String(100), index=True, nullable=True)
    
    def __repr__(self):
        return f"<HL7Message(id={self.id}, type={self.message_type}, status={self.status})>"


# EMR Connection Model
class EMRConnection(Base):
    __tablename__ = 'emr_connections'
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(String(100), unique=True, index=True)
    
    # EMR details
    emr_vendor = Column(String(50))  # Epic, Cerner, Meditech, etc.
    emr_version = Column(String(50))
    facility_name = Column(String(200))
    facility_id = Column(String(100))
    
    # Connection details
    base_url = Column(String(500), nullable=True)
    hl7_host = Column(String(200), nullable=True)
    hl7_port = Column(Integer, nullable=True)
    
    # Authentication (encrypted)
    client_id = Column(String(200), nullable=True)
    client_secret = Column(Text, nullable=True)  # Encrypted
    api_key = Column(Text, nullable=True)  # Encrypted
    
    # Status
    is_active = Column(Boolean, default=True)
    last_connected = Column(DateTime, nullable=True)
    connection_status = Column(String(50), default='disconnected')
    
    # Configuration
    config = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("HL7Message", backref="emr_connection")
    
    def __repr__(self):
        return f"<EMRConnection(id={self.id}, vendor={self.emr_vendor}, facility={self.facility_name})>"


# Incident Model
class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True)
    
    # Incident details
    incident_type = Column(String(50))  # message_failure, queue_backlog, etc.
    severity = Column(SQLEnum(IncidentSeverity))
    description = Column(Text)
    
    # Related message
    message_id = Column(Integer, ForeignKey('hl7_messages.id'), nullable=True)
    message = relationship("HL7Message", back_populates="incidents")
    
    # Detection
    detected_at = Column(DateTime, default=datetime.utcnow)
    detection_method = Column(String(50))  # automated, manual
    
    # Diagnosis
    root_cause = Column(Text, nullable=True)
    diagnosis_confidence = Column(Float, nullable=True)
    diagnosed_at = Column(DateTime, nullable=True)
    
    # Remediation
    remediation_actions = Column(JSON, nullable=True)
    remediation_status = Column(String(50), default='pending')
    remediated_at = Column(DateTime, nullable=True)
    
    # Resolution
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_time_seconds = Column(Integer, nullable=True)
    
    # Audit
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Incident(id={self.id}, type={self.incident_type}, severity={self.severity})>"


# Clinical Note Model
class ClinicalNote(Base):
    __tablename__ = 'clinical_notes'
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(String(100), unique=True, index=True)
    
    # Note details
    note_type = Column(String(50))  # soap, nursing, progress, etc.
    template_name = Column(String(100))
    
    # Patient information
    patient_id = Column(String(100), index=True)
    patient_name = Column(String(200))
    mrn = Column(String(100), index=True)
    
    # Provider information
    provider_id = Column(String(100), index=True)
    provider_name = Column(String(200))
    provider_role = Column(String(50))  # physician, nurse, therapist
    
    # Content
    content = Column(Text)
    structured_data = Column(JSON, nullable=True)
    
    # Generation
    generated_by_ai = Column(Boolean, default=False)
    ai_provider = Column(String(50), nullable=True)
    ai_model = Column(String(100), nullable=True)
    source = Column(String(50), default='manual')  # manual, voice, ai
    
    # Status
    status = Column(SQLEnum(NoteStatus), default=NoteStatus.DRAFT)
    
    # Signature
    signed = Column(Boolean, default=False)
    signature = Column(Text, nullable=True)
    signature_datetime = Column(DateTime, nullable=True)
    
    # Amendments
    amendments = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # EMR integration
    emr_uploaded = Column(Boolean, default=False)
    emr_document_id = Column(String(200), nullable=True)
    emr_upload_datetime = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ClinicalNote(id={self.id}, type={self.note_type}, patient={self.patient_name})>"


# AI Configuration Model
class AIConfiguration(Base):
    __tablename__ = 'ai_configurations'
    
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(String(100), unique=True, index=True)
    
    # Provider details
    provider = Column(String(50))  # openai, anthropic, google, etc.
    provider_display_name = Column(String(100))
    
    # API credentials (encrypted)
    api_key = Column(Text)  # Encrypted
    api_secret = Column(Text, nullable=True)  # Encrypted
    
    # Configuration
    default_model = Column(String(100))
    config = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIConfiguration(id={self.id}, provider={self.provider}, active={self.is_active})>"


# User Model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    
    # User details
    email = Column(String(200), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    full_name = Column(String(200))
    
    # Authentication
    hashed_password = Column(String(200))
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(200), nullable=True)
    
    # Role and permissions
    role = Column(String(50))  # admin, physician, nurse, therapist, analyst
    permissions = Column(JSON, default=list)
    
    # Provider information (if clinical user)
    provider_id = Column(String(100), nullable=True)
    provider_type = Column(String(50), nullable=True)  # MD, DO, RN, PA, NP, PT, OT
    npi_number = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# Audit Log Model
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(100), unique=True, index=True)
    
    # Event details
    event_type = Column(String(100))  # user_login, message_processed, note_created, etc.
    event_category = Column(String(50))  # authentication, data_access, system, etc.
    
    # User information
    user_id = Column(String(100), index=True, nullable=True)
    user_email = Column(String(200), nullable=True)
    user_role = Column(String(50), nullable=True)
    
    # Action details
    action = Column(String(100))  # create, read, update, delete
    resource_type = Column(String(50))  # message, note, patient, etc.
    resource_id = Column(String(100), nullable=True)
    
    # Result
    result = Column(String(50))  # success, failure
    error_message = Column(Text, nullable=True)
    
    # Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Data (encrypted for PHI)
    data_accessed = Column(JSON, nullable=True)
    changes_made = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # HIPAA compliance
    phi_accessed = Column(Boolean, default=False)
    justification = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event={self.event_type}, user={self.user_email})>"


# Monitoring Metrics Model
class MonitoringMetric(Base):
    __tablename__ = 'monitoring_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, index=True)
    
    # Metric details
    metric_name = Column(String(100), index=True)
    metric_type = Column(String(50))  # counter, gauge, histogram
    metric_value = Column(Float)
    
    # Context
    emr_connection_id = Column(String(100), nullable=True)
    interface_name = Column(String(100), nullable=True)
    
    # Metadata
    tags = Column(JSON, default=dict)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<MonitoringMetric(name={self.metric_name}, value={self.metric_value})>"


# SLA Log Model
class SLALog(Base):
    __tablename__ = 'sla_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(100), unique=True, index=True)
    
    # SLA details
    sla_name = Column(String(100))
    sla_type = Column(String(50))  # uptime, response_time, throughput
    
    # Measurement
    target_value = Column(Float)
    actual_value = Column(Float)
    met = Column(Boolean)
    
    # Context
    emr_connection_id = Column(String(100), nullable=True)
    interface_name = Column(String(100), nullable=True)
    
    # Time period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SLALog(name={self.sla_name}, met={self.met})>"


# Patient Cache Model (for quick lookups)
class PatientCache(Base):
    __tablename__ = 'patient_cache'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient identifiers
    patient_id = Column(String(100), index=True)
    mrn = Column(String(100), index=True)
    
    # Demographics
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(String(20))
    gender = Column(String(10))
    
    # Contact
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    address = Column(JSON, nullable=True)
    
    # EMR source
    emr_connection_id = Column(String(100))
    emr_patient_id = Column(String(100))
    
    # Cache metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    cache_expiry = Column(DateTime)
    
    def __repr__(self):
        return f"<PatientCache(mrn={self.mrn}, name={self.first_name} {self.last_name})>"


# Interface Status Model
class InterfaceStatus(Base):
    __tablename__ = 'interface_status'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Interface details
    interface_name = Column(String(100), unique=True, index=True)
    interface_type = Column(String(50))  # hl7, fhir, api
    
    # Connection
    emr_connection_id = Column(String(100))
    endpoint = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_healthy = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime, nullable=True)
    
    # Metrics
    messages_processed_today = Column(Integer, default=0)
    messages_failed_today = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, nullable=True)
    
    # Uptime
    uptime_percentage = Column(Float, default=100.0)
    last_downtime = Column(DateTime, nullable=True)
    downtime_duration_seconds = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<InterfaceStatus(name={self.interface_name}, healthy={self.is_healthy})>"


# Create all tables
def create_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


# Example usage
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create engine
    engine = create_engine('postgresql://user:pass@localhost:5432/itechsmart_hl7')
    
    # Create tables
    create_tables(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create sample HL7 message
    message = HL7Message(
        message_id='MSG001',
        message_type='ADT^A01',
        message_version='2.5',
        raw_message='MSH|^~\\&|...',
        sending_application='EPIC',
        receiving_application='ITECHSMART',
        status=MessageStatus.COMPLETED,
        patient_id='P123456'
    )
    
    session.add(message)
    session.commit()
    
    print(f"Created message: {message}")