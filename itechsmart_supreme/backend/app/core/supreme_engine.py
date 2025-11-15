"""
iTechSmart Supreme - Healthcare Management Engine
Comprehensive healthcare operations management
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from app.models.models import (
    Patient, Provider, Appointment, MedicalRecord, Prescription,
    Bill, Facility, Department, LabTest, Inventory,
    AppointmentStatus, PatientStatus, BillingStatus, PrescriptionStatus
)

logger = logging.getLogger(__name__)


class SupremeEngine:
    """
    Core healthcare management engine
    
    Features:
    - Patient management
    - Appointment scheduling
    - Medical records
    - Prescription management
    - Billing and insurance
    - Lab test tracking
    - Inventory management
    - Analytics and reporting
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Patient Management ====================
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Create new patient record"""
        try:
            # Generate MRN if not provided
            if "mrn" not in patient_data:
                patient_data["mrn"] = self._generate_mrn()
            
            patient = Patient(**patient_data)
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            
            logger.info(f"Created patient: {patient.mrn}")
            return patient
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating patient: {e}")
            raise
    
    def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    
    def search_patients(
        self,
        query: str = None,
        status: PatientStatus = None,
        limit: int = 100
    ) -> List[Patient]:
        """Search patients"""
        q = self.db.query(Patient)
        
        if query:
            search = f"%{query}%"
            q = q.filter(
                or_(
                    Patient.first_name.ilike(search),
                    Patient.last_name.ilike(search),
                    Patient.mrn.ilike(search),
                    Patient.email.ilike(search)
                )
            )
        
        if status:
            q = q.filter(Patient.status == status)
        
        return q.limit(limit).all()
    
    def update_patient(self, patient_id: int, updates: Dict[str, Any]) -> Patient:
        """Update patient information"""
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        for key, value in updates.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        
        patient.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(patient)
        
        return patient
    
    # ==================== Appointment Management ====================
    
    def schedule_appointment(self, appointment_data: Dict[str, Any]) -> Appointment:
        """Schedule new appointment"""
        try:
            # Check for conflicts
            conflicts = self._check_appointment_conflicts(
                appointment_data["provider_id"],
                appointment_data["appointment_date"],
                appointment_data.get("duration_minutes", 30)
            )
            
            if conflicts:
                raise ValueError("Appointment time conflicts with existing appointment")
            
            appointment = Appointment(**appointment_data)
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info(f"Scheduled appointment: {appointment.id}")
            return appointment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error scheduling appointment: {e}")
            raise
    
    def get_appointments(
        self,
        patient_id: int = None,
        provider_id: int = None,
        start_date: date = None,
        end_date: date = None,
        status: AppointmentStatus = None
    ) -> List[Appointment]:
        """Get appointments with filters"""
        q = self.db.query(Appointment)
        
        if patient_id:
            q = q.filter(Appointment.patient_id == patient_id)
        if provider_id:
            q = q.filter(Appointment.provider_id == provider_id)
        if start_date:
            q = q.filter(Appointment.appointment_date >= start_date)
        if end_date:
            q = q.filter(Appointment.appointment_date <= end_date)
        if status:
            q = q.filter(Appointment.status == status)
        
        return q.order_by(Appointment.appointment_date).all()
    
    def update_appointment_status(
        self,
        appointment_id: int,
        status: AppointmentStatus,
        notes: str = None
    ) -> Appointment:
        """Update appointment status"""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = status
        if notes:
            appointment.notes = notes
        appointment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    # ==================== Medical Records ====================
    
    def create_medical_record(self, record_data: Dict[str, Any]) -> MedicalRecord:
        """Create medical record"""
        try:
            record = MedicalRecord(**record_data)
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"Created medical record: {record.id}")
            return record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating medical record: {e}")
            raise
    
    def get_patient_medical_history(
        self,
        patient_id: int,
        limit: int = 50
    ) -> List[MedicalRecord]:
        """Get patient's medical history"""
        return self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).order_by(MedicalRecord.visit_date.desc()).limit(limit).all()
    
    # ==================== Prescription Management ====================
    
    def create_prescription(self, prescription_data: Dict[str, Any]) -> Prescription:
        """Create prescription"""
        try:
            prescription = Prescription(**prescription_data)
            self.db.add(prescription)
            self.db.commit()
            self.db.refresh(prescription)
            
            logger.info(f"Created prescription: {prescription.id}")
            return prescription
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating prescription: {e}")
            raise
    
    def get_active_prescriptions(self, patient_id: int) -> List[Prescription]:
        """Get patient's active prescriptions"""
        return self.db.query(Prescription).filter(
            and_(
                Prescription.patient_id == patient_id,
                Prescription.status == PrescriptionStatus.ACTIVE
            )
        ).all()
    
    # ==================== Billing Management ====================
    
    def create_bill(self, bill_data: Dict[str, Any]) -> Bill:
        """Create bill"""
        try:
            # Generate bill number if not provided
            if "bill_number" not in bill_data:
                bill_data["bill_number"] = self._generate_bill_number()
            
            # Calculate balance
            amount = bill_data.get("amount", 0)
            insurance_amount = bill_data.get("insurance_amount", 0)
            paid_amount = bill_data.get("paid_amount", 0)
            bill_data["patient_amount"] = amount - insurance_amount
            bill_data["balance"] = amount - paid_amount
            
            bill = Bill(**bill_data)
            self.db.add(bill)
            self.db.commit()
            self.db.refresh(bill)
            
            logger.info(f"Created bill: {bill.bill_number}")
            return bill
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating bill: {e}")
            raise
    
    def get_patient_bills(
        self,
        patient_id: int,
        status: BillingStatus = None
    ) -> List[Bill]:
        """Get patient bills"""
        q = self.db.query(Bill).filter(Bill.patient_id == patient_id)
        
        if status:
            q = q.filter(Bill.status == status)
        
        return q.order_by(Bill.service_date.desc()).all()
    
    def process_payment(
        self,
        bill_id: int,
        payment_amount: float
    ) -> Bill:
        """Process bill payment"""
        bill = self.db.query(Bill).filter(Bill.id == bill_id).first()
        
        if not bill:
            raise ValueError(f"Bill {bill_id} not found")
        
        bill.paid_amount += payment_amount
        bill.balance = bill.amount - bill.paid_amount
        
        if bill.balance <= 0:
            bill.status = BillingStatus.PAID
            bill.paid_date = date.today()
        
        bill.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(bill)
        
        return bill
    
    # ==================== Analytics & Reporting ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        today = date.today()
        
        # Patient stats
        total_patients = self.db.query(func.count(Patient.id)).scalar()
        active_patients = self.db.query(func.count(Patient.id)).filter(
            Patient.status == PatientStatus.ACTIVE
        ).scalar()
        
        # Appointment stats
        today_appointments = self.db.query(func.count(Appointment.id)).filter(
            func.date(Appointment.appointment_date) == today
        ).scalar()
        
        pending_appointments = self.db.query(func.count(Appointment.id)).filter(
            Appointment.status == AppointmentStatus.SCHEDULED
        ).scalar()
        
        # Billing stats
        pending_bills = self.db.query(func.sum(Bill.balance)).filter(
            Bill.status != BillingStatus.PAID
        ).scalar() or 0
        
        revenue_this_month = self.db.query(func.sum(Bill.paid_amount)).filter(
            func.extract('month', Bill.paid_date) == today.month,
            func.extract('year', Bill.paid_date) == today.year
        ).scalar() or 0
        
        return {
            "total_patients": total_patients,
            "active_patients": active_patients,
            "today_appointments": today_appointments,
            "pending_appointments": pending_appointments,
            "pending_bills_amount": float(pending_bills),
            "revenue_this_month": float(revenue_this_month),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_appointment_analytics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get appointment analytics"""
        appointments = self.get_appointments(
            start_date=start_date,
            end_date=end_date
        )
        
        by_status = {}
        by_provider = {}
        
        for apt in appointments:
            # By status
            status = apt.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # By provider
            provider_name = f"{apt.provider.first_name} {apt.provider.last_name}"
            by_provider[provider_name] = by_provider.get(provider_name, 0) + 1
        
        return {
            "total_appointments": len(appointments),
            "by_status": by_status,
            "by_provider": by_provider,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    # ==================== Helper Methods ====================
    
    def _generate_mrn(self) -> str:
        """Generate unique Medical Record Number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        count = self.db.query(func.count(Patient.id)).scalar()
        return f"MRN{timestamp}{count:04d}"
    
    def _generate_bill_number(self) -> str:
        """Generate unique bill number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        count = self.db.query(func.count(Bill.id)).scalar()
        return f"BILL{timestamp}{count:04d}"
    
    def _check_appointment_conflicts(
        self,
        provider_id: int,
        appointment_date: datetime,
        duration_minutes: int
    ) -> List[Appointment]:
        """Check for appointment conflicts"""
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        conflicts = self.db.query(Appointment).filter(
            and_(
                Appointment.provider_id == provider_id,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.IN_PROGRESS
                ]),
                or_(
                    and_(
                        Appointment.appointment_date <= appointment_date,
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) > appointment_date
                    ),
                    and_(
                        Appointment.appointment_date < end_time,
                        Appointment.appointment_date >= appointment_date
                    )
                )
            )
        ).all()
        
        return conflicts