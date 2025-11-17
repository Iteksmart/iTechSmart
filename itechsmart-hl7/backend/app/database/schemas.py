"""
Pydantic Schemas
Data validation and serialization schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class ObservationTypeEnum(str, Enum):
    VITAL_SIGNS = "vital-signs"
    LABORATORY = "laboratory"
    SOCIAL_HISTORY = "social-history"
    EXAM = "exam"
    IMAGING = "imaging"
    PROCEDURE = "procedure"


class MedicationStatusEnum(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ON_HOLD = "on-hold"
    CANCELLED = "cancelled"


class AllergyTypeEnum(str, Enum):
    ALLERGY = "allergy"
    INTOLERANCE = "intolerance"


class AllergyCategoryEnum(str, Enum):
    FOOD = "food"
    MEDICATION = "medication"
    ENVIRONMENT = "environment"
    BIOLOGIC = "biologic"


class HL7DirectionEnum(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class HL7StatusEnum(str, Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    ERROR = "error"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"


# Base Schemas


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


# Patient Schemas


class PatientBase(BaseSchema):
    mrn: str = Field(..., description="Medical Record Number")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    birth_date: Optional[datetime] = None
    ssn: Optional[str] = None
    phone_home: Optional[str] = None
    phone_work: Optional[str] = None
    phone_mobile: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    marital_status: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    language: Optional[str] = None


class PatientCreate(PatientBase):
    source_emr: str
    source_patient_id: str
    raw_data: Optional[Dict[str, Any]] = None


class PatientUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    birth_date: Optional[datetime] = None
    phone_home: Optional[str] = None
    phone_mobile: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class PatientResponse(PatientBase):
    id: str
    full_name: Optional[str] = None
    source_emr: str
    source_patient_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


# Observation Schemas


class ObservationBase(BaseSchema):
    observation_type: ObservationTypeEnum
    code_system: Optional[str] = None
    code: str
    code_display: Optional[str] = None
    value_quantity: Optional[float] = None
    value_string: Optional[str] = None
    value_boolean: Optional[bool] = None
    unit: Optional[str] = None
    status: str
    effective_datetime: Optional[datetime] = None


class ObservationCreate(ObservationBase):
    patient_id: str
    source_emr: str
    source_observation_id: str
    raw_data: Optional[Dict[str, Any]] = None


class ObservationResponse(ObservationBase):
    id: str
    patient_id: str
    source_emr: str
    interpretation_code: Optional[str] = None
    abnormal_flag: Optional[str] = None
    created_at: datetime


# Medication Schemas


class MedicationBase(BaseSchema):
    medication_name: str
    generic_name: Optional[str] = None
    code: Optional[str] = None
    dosage_text: Optional[str] = None
    strength: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    status: MedicationStatusEnum
    intent: Optional[str] = None


class MedicationCreate(MedicationBase):
    patient_id: str
    source_emr: str
    source_medication_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None


class MedicationResponse(MedicationBase):
    id: str
    patient_id: str
    source_emr: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prescriber_name: Optional[str] = None
    created_at: datetime


# Allergy Schemas


class AllergyBase(BaseSchema):
    allergen: str
    code: Optional[str] = None
    allergy_type: AllergyTypeEnum
    category: AllergyCategoryEnum
    clinical_status: str
    verification_status: Optional[str] = None
    criticality: Optional[str] = None


class AllergyCreate(AllergyBase):
    patient_id: str
    source_emr: str
    source_allergy_id: str
    reaction_manifestation: Optional[str] = None
    reaction_severity: Optional[str] = None
    onset_date: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None


class AllergyResponse(AllergyBase):
    id: str
    patient_id: str
    source_emr: str
    reaction_manifestation: Optional[str] = None
    reaction_severity: Optional[str] = None
    onset_date: Optional[datetime] = None
    created_at: datetime


# HL7 Message Schemas


class HL7MessageBase(BaseSchema):
    message_type: str
    message_control_id: str
    direction: HL7DirectionEnum
    raw_message: str


class HL7MessageCreate(HL7MessageBase):
    patient_mrn: Optional[str] = None
    sending_application: Optional[str] = None
    sending_facility: Optional[str] = None
    receiving_application: Optional[str] = None
    receiving_facility: Optional[str] = None
    connection_id: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


class HL7MessageResponse(HL7MessageBase):
    id: str
    status: HL7StatusEnum
    ack_status: Optional[str] = None
    patient_id: Optional[str] = None
    patient_mrn: Optional[str] = None
    connection_id: Optional[str] = None
    error_message: Optional[str] = None
    message_datetime: Optional[datetime] = None
    received_at: datetime
    processed_at: Optional[datetime] = None


# EMR Connection Schemas


class EMRConnectionBase(BaseSchema):
    connection_id: str
    emr_type: str
    name: str
    description: Optional[str] = None


class EMRConnectionCreate(EMRConnectionBase):
    config: Dict[str, Any]
    created_by: Optional[str] = None


class EMRConnectionUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class EMRConnectionResponse(EMRConnectionBase):
    id: str
    is_active: bool
    is_connected: bool
    last_connection_test: Optional[datetime] = None
    last_connection_status: Optional[str] = None
    total_requests: int
    successful_requests: int
    failed_requests: int
    created_at: datetime
    updated_at: datetime


# Audit Log Schemas


class AuditLogBase(BaseSchema):
    event_type: str
    event_category: str
    action: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    patient_id: Optional[str] = None
    patient_mrn: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    status: str
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None


class AuditLogResponse(AuditLogBase):
    id: str
    patient_id: Optional[str] = None
    patient_mrn: Optional[str] = None
    status: str
    timestamp: datetime


# Aggregated Data Schemas


class AggregatedPatientData(BaseSchema):
    demographics: Optional[PatientResponse] = None
    observations: List[ObservationResponse] = []
    medications: List[MedicationResponse] = []
    allergies: List[AllergyResponse] = []
    sources: List[str] = []


# Search Schemas


class PatientSearchCriteria(BaseSchema):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[GenderEnum] = None
    mrn: Optional[str] = None
    ssn: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ObservationSearchCriteria(BaseSchema):
    patient_id: str
    observation_type: Optional[ObservationTypeEnum] = None
    code: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Statistics Schemas


class ConnectionStatistics(BaseSchema):
    total_connections: int
    active_connections: int
    connections_by_type: Dict[str, int]
    connection_list: List[Dict[str, Any]]


class SystemStatistics(BaseSchema):
    total_patients: int
    total_observations: int
    total_medications: int
    total_allergies: int
    total_hl7_messages: int
    active_connections: int
    database_health: Dict[str, Any]
    redis_health: Dict[str, Any]
