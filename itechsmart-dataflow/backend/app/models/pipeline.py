"""
Pipeline data models
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    JSON,
    Boolean,
    Float,
    Text,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import enum

Base = declarative_base()


class PipelineStatus(str, enum.Enum):
    """Pipeline status enum"""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class PipelineType(str, enum.Enum):
    """Pipeline type enum"""

    BATCH = "batch"
    STREAMING = "streaming"
    INCREMENTAL = "incremental"
    FULL_REFRESH = "full_refresh"


class Pipeline(Base):
    """Pipeline database model"""

    __tablename__ = "pipelines"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum(PipelineType), default=PipelineType.BATCH)
    status = Column(Enum(PipelineStatus), default=PipelineStatus.DRAFT)

    # Source configuration
    source_type = Column(String, nullable=False)
    source_config = Column(JSON, nullable=False)

    # Destination configuration
    destination_type = Column(String, nullable=False)
    destination_config = Column(JSON, nullable=False)

    # Transformation configuration
    transformations = Column(JSON, default=[])

    # Schedule
    schedule = Column(String)  # Cron expression

    # Metadata
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Statistics
    last_run_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)

    # Performance
    avg_duration_seconds = Column(Float)
    success_rate = Column(Float)

    # Settings
    enabled = Column(Boolean, default=True)
    retry_enabled = Column(Boolean, default=True)
    retry_attempts = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=3600)

    # Integration
    integration_config = Column(JSON, default={})


class PipelineRun(Base):
    """Pipeline run database model"""

    __tablename__ = "pipeline_runs"

    id = Column(String, primary_key=True)
    pipeline_id = Column(String, nullable=False)

    status = Column(Enum(PipelineStatus), default=PipelineStatus.RUNNING)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    records_read = Column(Integer, default=0)
    records_written = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    error_message = Column(Text)
    error_details = Column(JSON)

    logs = Column(JSON, default=[])
    metrics = Column(JSON, default={})


# Pydantic models for API


class SourceConfig(BaseModel):
    """Source configuration"""

    type: str
    config: Dict[str, Any]


class DestinationConfig(BaseModel):
    """Destination configuration"""

    type: str
    config: Dict[str, Any]


class TransformationConfig(BaseModel):
    """Transformation configuration"""

    type: str
    config: Dict[str, Any]


class PipelineCreate(BaseModel):
    """Pipeline creation schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: PipelineType = PipelineType.BATCH

    source: SourceConfig
    destination: DestinationConfig
    transformations: List[TransformationConfig] = []

    schedule: Optional[str] = None

    retry_enabled: bool = True
    retry_attempts: int = 3
    timeout_seconds: int = 3600


class PipelineUpdate(BaseModel):
    """Pipeline update schema"""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PipelineStatus] = None

    source: Optional[SourceConfig] = None
    destination: Optional[DestinationConfig] = None
    transformations: Optional[List[TransformationConfig]] = None

    schedule: Optional[str] = None

    retry_enabled: Optional[bool] = None
    retry_attempts: Optional[int] = None
    timeout_seconds: Optional[int] = None


class PipelineResponse(BaseModel):
    """Pipeline response schema"""

    id: str
    name: str
    description: Optional[str]
    type: PipelineType
    status: PipelineStatus

    source: SourceConfig
    destination: DestinationConfig
    transformations: List[TransformationConfig]

    schedule: Optional[str]

    created_at: datetime
    updated_at: datetime

    last_run_at: Optional[datetime]
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: Optional[float]

    class Config:
        from_attributes = True


class PipelineRunResponse(BaseModel):
    """Pipeline run response schema"""

    id: str
    pipeline_id: str
    status: PipelineStatus

    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]

    records_read: int
    records_written: int
    records_failed: int

    error_message: Optional[str]

    class Config:
        from_attributes = True
