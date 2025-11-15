"""
iTechSmart Supreme - Database Models
Healthcare Management System
"""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PatientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"


class BillingStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PAID = "paid"
    DENIED = "denied"
    APPEALED = "appealed"


class PrescriptionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Patient(Base):
    """Patient information"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    mrn = Column(String(50), unique=True, index=True, nullable=False)  # Medical Record Number
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))
    ssn = Column(String(11))  # Encrypted
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    insurance_provider = Column(String(200))
    insurance_policy_number = Column(String(100))
    insurance_group_number = Column(String(100))
    status = Column(SQLEnum(PatientStatus), default=PatientStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")


class Provider(Base):
    """Healthcare provider information"""
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    npi = Column(String(10), unique=True, index=True)  # National Provider Identifier
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(200))
    license_number = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    department = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="provider")
    medical_records = relationship("MedicalRecord", back_populates="provider")
    prescriptions = relationship("Prescription", back_populates="provider")


class Appointment(Base):
    """Patient appointments"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    reason = Column(Text)
    notes = Column(Text)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    room_number = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("Provider", back_populates="appointments")


class MedicalRecord(Base):
    """Patient medical records"""
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    chief_complaint = Column(Text)
    diagnosis = Column(Text)
    treatment = Column(Text)
    vital_signs = Column(Text)  # JSON string
    lab_results = Column(Text)  # JSON string
    imaging_results = Column(Text)  # JSON string
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    provider = relationship("Provider", back_populates="medical_records")


class Prescription(Base):
    """Patient prescriptions"""
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    medication_name = Column(String(200), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration = Column(String(100))
    quantity = Column(Integer)
    refills = Column(Integer, default=0)
    instructions = Column(Text)
    status = Column(SQLEnum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE)
    prescribed_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    provider = relationship("Provider", back_populates="prescriptions")


class Bill(Base):
    """Patient billing"""
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    bill_number = Column(String(50), unique=True, index=True)
    service_date = Column(Date, nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    insurance_amount = Column(Float, default=0.0)
    patient_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    status = Column(SQLEnum(BillingStatus), default=BillingStatus.PENDING)
    due_date = Column(Date)
    paid_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="bills")


class Facility(Base):
    """Healthcare facility information"""
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    facility_type = Column(String(100))  # Hospital, Clinic, Lab, etc.
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    phone = Column(String(20))
    email = Column(String(255))
    capacity = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Department(Base):
    """Hospital departments"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    head_provider_id = Column(Integer, ForeignKey("providers.id"))
    phone = Column(String(20))
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LabTest(Base):
    """Laboratory tests"""
    __tablename__ = "lab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    test_name = Column(String(200), nullable=False)
    test_code = Column(String(50))
    ordered_date = Column(DateTime, default=datetime.utcnow)
    collected_date = Column(DateTime)
    completed_date = Column(DateTime)
    results = Column(Text)
    normal_range = Column(String(200))
    status = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Inventory(Base):
    """Medical inventory management"""
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(200), nullable=False)
    item_code = Column(String(50), unique=True, index=True)
    category = Column(String(100))
    quantity = Column(Integer, default=0)
    unit = Column(String(50))
    reorder_level = Column(Integer, default=10)
    unit_cost = Column(Float)
    supplier = Column(String(200))
    expiry_date = Column(Date)
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)