"""
iTechSmart Port Manager - Database Models
Dynamic Port Configuration System
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PortStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    RESERVED = "reserved"
    CONFLICT = "conflict"


class ServiceStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Service(Base):
    """Service information"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text)
    current_port = Column(Integer, nullable=False)
    default_port = Column(Integer)
    status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.UNKNOWN)
    health_endpoint = Column(String(500))
    last_health_check = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    port_assignments = relationship("PortAssignment", back_populates="service")
    conflicts = relationship("PortConflict", back_populates="service")


class Port(Base):
    """Port information"""
    __tablename__ = "ports"
    
    id = Column(Integer, primary_key=True, index=True)
    port_number = Column(Integer, nullable=False, unique=True, index=True)
    status = Column(SQLEnum(PortStatus), default=PortStatus.AVAILABLE)
    service_id = Column(Integer, ForeignKey("services.id"))
    is_system_port = Column(Boolean, default=False)  # Ports < 1024
    is_reserved = Column(Boolean, default=False)
    reserved_for = Column(String(200))
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = relationship("PortAssignment", back_populates="port")


class PortAssignment(Base):
    """Port assignment history"""
    __tablename__ = "port_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    port_id = Column(Integer, ForeignKey("ports.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    reason = Column(Text)
    
    # Relationships
    service = relationship("Service", back_populates="port_assignments")
    port = relationship("Port", back_populates="assignments")


class PortConflict(Base):
    """Port conflict detection"""
    __tablename__ = "port_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    port_number = Column(Integer, nullable=False)
    conflicting_service = Column(String(200))
    severity = Column(SQLEnum(ConflictSeverity), default=ConflictSeverity.MEDIUM)
    description = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_method = Column(String(200))
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="conflicts")


class PortRange(Base):
    """Port range configuration"""
    __tablename__ = "port_ranges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    start_port = Column(Integer, nullable=False)
    end_port = Column(Integer, nullable=False)
    purpose = Column(String(200))
    is_reserved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Configuration(Base):
    """Port manager configuration"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(200), nullable=False, unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HealthCheck(Base):
    """Service health check results"""
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String(50))
    response_time = Column(Integer)  # milliseconds
    error_message = Column(Text)
    checked_at = Column(DateTime, default=datetime.utcnow)


class PortStatistic(Base):
    """Port usage statistics"""
    __tablename__ = "port_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    port_number = Column(Integer, nullable=False)
    service_name = Column(String(200))
    usage_count = Column(Integer, default=0)
    total_uptime = Column(Integer, default=0)  # seconds
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)