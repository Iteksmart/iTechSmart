"""
Database Models
SQLAlchemy models for PostgreSQL
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    Index,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Patient(Base):
    """
    Patient model - stores patient demographics
    """

    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mrn = Column(String(50), unique=True, nullable=False, index=True)

    # Demographics
    first_name = Column(String(100))
    last_name = Column(String(100))
    middle_name = Column(String(100))
    full_name = Column(String(300))

    gender = Column(String(20))
    birth_date = Column(DateTime)
    ssn = Column(String(11))

    # Contact Information
    phone_home = Column(String(20))
    phone_work = Column(String(20))
    phone_mobile = Column(String(20))
    email = Column(String(255))

    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100))

    # Additional Information
    marital_status = Column(String(50))
    race = Column(String(100))
    ethnicity = Column(String(100))
    language = Column(String(50))

    # EMR Source Information
    source_emr = Column(String(50))
    source_patient_id = Column(String(100))

    # Metadata
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    observations = relationship(
        "Observation", back_populates="patient", cascade="all, delete-orphan"
    )
    medications = relationship(
        "Medication", back_populates="patient", cascade="all, delete-orphan"
    )
    allergies = relationship(
        "Allergy", back_populates="patient", cascade="all, delete-orphan"
    )
    hl7_messages = relationship(
        "HL7Message", back_populates="patient", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_patient_name", "last_name", "first_name"),
        Index("idx_patient_birth_date", "birth_date"),
        Index("idx_patient_source", "source_emr", "source_patient_id"),
    )

    def __repr__(self):
        return f"<Patient(mrn='{self.mrn}', name='{self.full_name}')>"


class Observation(Base):
    """
    Observation model - stores patient observations (vitals, labs, etc.)
    """

    __tablename__ = "observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    # Observation Details
    observation_type = Column(String(50))  # vital-signs, laboratory, etc.
    code_system = Column(String(100))
    code = Column(String(50))
    code_display = Column(String(255))

    # Value
    value_type = Column(String(50))  # quantity, string, boolean, codeable_concept
    value_quantity = Column(Float)
    value_string = Column(Text)
    value_boolean = Column(Boolean)
    value_code = Column(String(100))
    unit = Column(String(50))

    # Status and Timing
    status = Column(String(50))
    effective_datetime = Column(DateTime)
    issued_datetime = Column(DateTime)

    # Reference Range
    reference_range_low = Column(Float)
    reference_range_high = Column(Float)
    reference_range_text = Column(String(255))

    # Interpretation
    interpretation_code = Column(String(50))
    interpretation_display = Column(String(255))
    abnormal_flag = Column(String(10))

    # Source Information
    source_emr = Column(String(50))
    source_observation_id = Column(String(100))
    performer = Column(String(255))

    # Metadata
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="observations")

    # Indexes
    __table_args__ = (
        Index("idx_observation_patient", "patient_id"),
        Index("idx_observation_type", "observation_type"),
        Index("idx_observation_code", "code"),
        Index("idx_observation_date", "effective_datetime"),
    )

    def __repr__(self):
        return f"<Observation(patient_id='{self.patient_id}', code='{self.code}', value='{self.value_quantity}')>"


class Medication(Base):
    """
    Medication model - stores patient medications
    """

    __tablename__ = "medications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    # Medication Details
    medication_name = Column(String(255))
    generic_name = Column(String(255))
    code_system = Column(String(100))
    code = Column(String(50))

    # Dosage
    dosage_text = Column(Text)
    strength = Column(String(100))
    dose_quantity = Column(Float)
    dose_unit = Column(String(50))

    # Route and Frequency
    route = Column(String(100))
    frequency = Column(String(100))
    frequency_code = Column(String(50))

    # Status and Timing
    status = Column(String(50))
    intent = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    authored_on = Column(DateTime)

    # Prescriber Information
    prescriber_name = Column(String(255))
    prescriber_id = Column(String(100))
    pharmacy = Column(String(255))

    # Source Information
    source_emr = Column(String(50))
    source_medication_id = Column(String(100))

    # Metadata
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="medications")

    # Indexes
    __table_args__ = (
        Index("idx_medication_patient", "patient_id"),
        Index("idx_medication_name", "medication_name"),
        Index("idx_medication_status", "status"),
        Index("idx_medication_date", "start_date"),
    )

    def __repr__(self):
        return f"<Medication(patient_id='{self.patient_id}', name='{self.medication_name}')>"


class Allergy(Base):
    """
    Allergy model - stores patient allergies and intolerances
    """

    __tablename__ = "allergies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)

    # Allergy Details
    allergen = Column(String(255))
    code_system = Column(String(100))
    code = Column(String(50))

    # Type and Category
    allergy_type = Column(String(50))  # allergy, intolerance
    category = Column(String(50))  # food, medication, environment, biologic

    # Status
    clinical_status = Column(String(50))
    verification_status = Column(String(50))
    criticality = Column(String(50))  # low, high, unable-to-assess

    # Reaction
    reaction_manifestation = Column(Text)
    reaction_severity = Column(String(50))
    reaction_description = Column(Text)

    # Timing
    onset_date = Column(DateTime)
    recorded_date = Column(DateTime)

    # Source Information
    source_emr = Column(String(50))
    source_allergy_id = Column(String(100))
    recorder = Column(String(255))

    # Metadata
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="allergies")

    # Indexes
    __table_args__ = (
        Index("idx_allergy_patient", "patient_id"),
        Index("idx_allergy_allergen", "allergen"),
        Index("idx_allergy_criticality", "criticality"),
    )

    def __repr__(self):
        return f"<Allergy(patient_id='{self.patient_id}', allergen='{self.allergen}')>"


class HL7Message(Base):
    """
    HL7 Message model - stores HL7 v2.x messages
    """

    __tablename__ = "hl7_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Message Details
    message_type = Column(String(20), nullable=False)  # ADT^A01, ORU^R01, etc.
    message_control_id = Column(String(100), unique=True, nullable=False)

    # Direction
    direction = Column(String(10))  # inbound, outbound

    # Content
    raw_message = Column(Text, nullable=False)
    parsed_data = Column(JSON)

    # Status
    status = Column(String(50))  # received, processed, error, sent, acknowledged
    ack_status = Column(String(10))  # AA, AE, AR
    ack_message = Column(Text)

    # Patient Reference
    patient_id = Column(String(36), ForeignKey("patients.id"))
    patient_mrn = Column(String(50))

    # Source/Destination
    sending_application = Column(String(100))
    sending_facility = Column(String(100))
    receiving_application = Column(String(100))
    receiving_facility = Column(String(100))

    # Connection
    connection_id = Column(String(100))

    # Error Handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Timing
    message_datetime = Column(DateTime)
    received_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="hl7_messages")

    # Indexes
    __table_args__ = (
        Index("idx_hl7_message_type", "message_type"),
        Index("idx_hl7_direction", "direction"),
        Index("idx_hl7_status", "status"),
        Index("idx_hl7_patient", "patient_id"),
        Index("idx_hl7_datetime", "message_datetime"),
        Index("idx_hl7_connection", "connection_id"),
    )

    def __repr__(self):
        return f"<HL7Message(type='{self.message_type}', control_id='{self.message_control_id}')>"


class EMRConnection(Base):
    """
    EMR Connection model - stores EMR connection configurations
    """

    __tablename__ = "emr_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Connection Details
    connection_id = Column(String(100), unique=True, nullable=False)
    emr_type = Column(String(50), nullable=False)  # epic, cerner, meditech, etc.
    name = Column(String(255))
    description = Column(Text)

    # Configuration (encrypted in production)
    config = Column(JSON, nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_connection_test = Column(DateTime)
    last_connection_status = Column(String(50))

    # Statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_request_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Indexes
    __table_args__ = (
        Index("idx_connection_type", "emr_type"),
        Index("idx_connection_active", "is_active"),
    )

    def __repr__(self):
        return f"<EMRConnection(id='{self.connection_id}', type='{self.emr_type}')>"


class AuditLog(Base):
    """
    Audit Log model - stores all system activities for HIPAA compliance
    """

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Event Details
    event_type = Column(
        String(50), nullable=False
    )  # login, access, modify, delete, etc.
    event_category = Column(
        String(50)
    )  # authentication, data_access, configuration, etc.
    action = Column(String(100), nullable=False)

    # User Information
    user_id = Column(String(100))
    username = Column(String(100))
    user_role = Column(String(50))

    # Resource Information
    resource_type = Column(String(50))  # patient, observation, medication, etc.
    resource_id = Column(String(100))

    # Patient Reference (for PHI access tracking)
    patient_id = Column(String(36))
    patient_mrn = Column(String(50))

    # Request Details
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    request_method = Column(String(10))
    request_path = Column(String(500))

    # Result
    status = Column(String(50))  # success, failure, error
    status_code = Column(Integer)
    error_message = Column(Text)

    # Additional Data
    details = Column(JSON)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_ms = Column(Integer)

    # Indexes
    __table_args__ = (
        Index("idx_audit_event_type", "event_type"),
        Index("idx_audit_user", "username"),
        Index("idx_audit_patient", "patient_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )

    def __repr__(self):
        return f"<AuditLog(event='{self.event_type}', user='{self.username}', timestamp='{self.timestamp}')>"
