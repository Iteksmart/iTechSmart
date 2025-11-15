"""
Database models for LegalAI Pro
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ATTORNEY = "attorney"
    PARALEGAL = "paralegal"
    STAFF = "staff"
    CLIENT = "client"

class CaseStatus(str, enum.Enum):
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"
    ARCHIVED = "archived"

class CaseType(str, enum.Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    FAMILY = "family"
    CORPORATE = "corporate"
    REAL_ESTATE = "real_estate"
    IMMIGRATION = "immigration"
    BANKRUPTCY = "bankruptcy"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    EMPLOYMENT = "employment"
    OTHER = "other"

class BillingStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF)
    phone = Column(String)
    bar_number = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cases = relationship("Case", back_populates="attorney")
    time_entries = relationship("TimeEntry", back_populates="user")
    tasks = relationship("Task", back_populates="assigned_to_user")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    mobile = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String, default="USA")
    ssn = Column(String)  # Encrypted in production
    date_of_birth = Column(DateTime)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cases = relationship("Case", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    case_type = Column(Enum(CaseType), nullable=False)
    status = Column(Enum(CaseStatus), default=CaseStatus.OPEN)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    attorney_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    court_name = Column(String)
    judge_name = Column(String)
    opposing_party = Column(String)
    opposing_counsel = Column(String)
    filing_date = Column(DateTime)
    statute_of_limitations = Column(DateTime)
    trial_date = Column(DateTime)
    settlement_amount = Column(Float)
    hourly_rate = Column(Float)
    flat_fee = Column(Float)
    contingency_percentage = Column(Float)
    retainer_amount = Column(Float)
    custom_fields = Column(JSON)  # For flexible data storage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="cases")
    attorney = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case")
    time_entries = relationship("TimeEntry", back_populates="case")
    tasks = relationship("Task", back_populates="case")
    calendar_events = relationship("CalendarEvent", back_populates="case")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    file_size = Column(Integer)
    category = Column(String)
    tags = Column(JSON)
    version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False)
    ai_summary = Column(Text)  # AI-generated summary
    ai_extracted_data = Column(JSON)  # AI-extracted key information
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="documents")

class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    hours = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    is_billable = Column(Boolean, default=True)
    is_billed = Column(Boolean, default=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="time_entries")
    user = relationship("User", back_populates="time_entries")
    invoice = relationship("Invoice", back_populates="time_entries")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"))
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(BillingStatus), default=BillingStatus.DRAFT)
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    time_entries = relationship("TimeEntry", back_populates="invoice")
    expenses = relationship("Expense", back_populates="invoice")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)
    receipt_path = Column(String)
    is_billable = Column(Boolean, default=True)
    is_billed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="expenses")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="tasks")
    assigned_to_user = relationship("User", back_populates="tasks")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)
    event_type = Column(String)  # hearing, deposition, meeting, deadline, etc.
    attendees = Column(JSON)
    reminder_minutes = Column(Integer, default=30)
    is_all_day = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="calendar_events")

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    template_type = Column(String)  # document, email, contract, etc.
    content = Column(Text, nullable=False)
    variables = Column(JSON)  # List of variables that can be auto-filled
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"))
    conversation_type = Column(String)  # research, document_review, case_analysis, etc.
    messages = Column(JSON)  # Array of messages
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())