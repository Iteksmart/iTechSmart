"""
iTechSmart Sandbox - Database Models
Secure Code Execution Environment
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SandboxStatus(str, Enum):
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    ERROR = "error"


class ProcessStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


class SnapshotStatus(str, Enum):
    CREATING = "creating"
    READY = "ready"
    FAILED = "failed"


class ResourceType(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"


class Sandbox(Base):
    """Sandbox instance"""
    __tablename__ = "sandboxes"
    
    id = Column(Integer, primary_key=True, index=True)
    sandbox_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200))
    description = Column(Text)
    image = Column(String(500))  # Docker image
    cpu = Column(Float, default=1.0)
    memory = Column(String(20), default="1Gi")
    gpu = Column(String(50))  # GPU type (A10G, T4, etc.)
    status = Column(SQLEnum(SandboxStatus), default=SandboxStatus.CREATING)
    
    # Configuration
    python_version = Column(String(20))
    packages = Column(JSON)  # Python packages
    env_vars = Column(JSON)  # Environment variables
    secrets = Column(JSON)  # Secret names
    
    # Networking
    exposed_ports = Column(JSON)  # List of exposed ports
    preview_urls = Column(JSON)  # Port -> URL mapping
    
    # Storage
    volumes = Column(JSON)  # Mounted volumes
    workspace_path = Column(String(500), default="/workspace")
    
    # Lifecycle
    keep_warm_seconds = Column(Integer, default=3600)  # 1 hour default
    auto_terminate = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    terminated_at = Column(DateTime)
    last_activity = Column(DateTime)
    
    # Metadata
    created_by = Column(String(200))
    project_id = Column(Integer, ForeignKey("projects.id"))
    tags = Column(JSON)
    
    # Relationships
    processes = relationship("Process", back_populates="sandbox")
    snapshots = relationship("Snapshot", back_populates="sandbox")
    files = relationship("SandboxFile", back_populates="sandbox")
    metrics = relationship("ResourceMetric", back_populates="sandbox")


class Process(Base):
    """Process running in sandbox"""
    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True, index=True)
    sandbox_id = Column(Integer, ForeignKey("sandboxes.id"), nullable=False)
    process_id = Column(String(100), unique=True, index=True)
    command = Column(Text, nullable=False)
    args = Column(JSON)
    cwd = Column(String(500))
    status = Column(SQLEnum(ProcessStatus), default=ProcessStatus.RUNNING)
    exit_code = Column(Integer)
    stdout = Column(Text)
    stderr = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    sandbox = relationship("Sandbox", back_populates="processes")


class Snapshot(Base):
    """Sandbox filesystem snapshot"""
    __tablename__ = "snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    sandbox_id = Column(Integer, ForeignKey("sandboxes.id"), nullable=False)
    snapshot_id = Column(String(100), unique=True, index=True)
    name = Column(String(200))
    description = Column(Text)
    size_bytes = Column(Integer)
    status = Column(SQLEnum(SnapshotStatus), default=SnapshotStatus.CREATING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sandbox = relationship("Sandbox", back_populates="snapshots")


class SandboxFile(Base):
    """Files in sandbox"""
    __tablename__ = "sandbox_files"
    
    id = Column(Integer, primary_key=True, index=True)
    sandbox_id = Column(Integer, ForeignKey("sandboxes.id"), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(100))
    content_hash = Column(String(64))  # SHA-256
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sandbox = relationship("Sandbox", back_populates="files")


class ResourceMetric(Base):
    """Resource usage metrics"""
    __tablename__ = "resource_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    sandbox_id = Column(Integer, ForeignKey("sandboxes.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)  # Percentage
    memory_usage = Column(Float)  # Percentage
    memory_bytes = Column(Integer)
    gpu_usage = Column(Float)  # Percentage
    disk_usage = Column(Float)  # Percentage
    network_in = Column(Integer)  # Bytes
    network_out = Column(Integer)  # Bytes
    
    # Relationships
    sandbox = relationship("Sandbox", back_populates="metrics")


class Project(Base):
    """Project grouping for sandboxes"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    owner = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Template(Base):
    """Sandbox templates"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    image = Column(String(500))
    cpu = Column(Float)
    memory = Column(String(20))
    gpu = Column(String(50))
    packages = Column(JSON)
    env_vars = Column(JSON)
    is_public = Column(Boolean, default=False)
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


class Volume(Base):
    """Persistent storage volume"""
    __tablename__ = "volumes"
    
    id = Column(Integer, primary_key=True, index=True)
    volume_id = Column(String(100), unique=True, index=True)
    name = Column(String(200), nullable=False)
    mount_path = Column(String(500))
    size_gb = Column(Integer)
    used_gb = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestRun(Base):
    """Test execution record"""
    __tablename__ = "test_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    sandbox_id = Column(Integer, ForeignKey("sandboxes.id"), nullable=False)
    test_suite = Column(String(200))
    product_name = Column(String(200))  # iTechSmart product being tested
    test_type = Column(String(100))  # unit, integration, e2e, performance
    total_tests = Column(Integer)
    passed_tests = Column(Integer)
    failed_tests = Column(Integer)
    skipped_tests = Column(Integer)
    duration_seconds = Column(Float)
    results = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)