"""
iTechSmart Analytics - Database Models
ML-Powered Analytics Platform
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DataSourceType(str, Enum):
    REST_API = "rest_api"
    DATABASE = "database"
    KAFKA = "kafka"
    WEBHOOK = "webhook"
    FILE = "file"
    STREAM = "stream"


class IngestionMode(str, Enum):
    REALTIME = "realtime"
    BATCH = "batch"
    SCHEDULED = "scheduled"


class AnalysisType(str, Enum):
    FORECASTING = "forecasting"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ANALYSIS = "trend_analysis"
    CORRELATION = "correlation"
    SEGMENTATION = "segmentation"
    COHORT = "cohort"


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class DataSource(Base):
    """Data source configuration"""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    source_type = Column(SQLEnum(DataSourceType), nullable=False)
    connection_string = Column(Text)
    config = Column(JSON)  # Source-specific configuration
    ingestion_mode = Column(SQLEnum(IngestionMode), default=IngestionMode.BATCH)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    datasets = relationship("Dataset", back_populates="data_source")


class Dataset(Base):
    """Dataset information"""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"))
    schema = Column(JSON)  # Dataset schema
    row_count = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    last_updated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    data_source = relationship("DataSource", back_populates="datasets")
    analyses = relationship("Analysis", back_populates="dataset")


class Dashboard(Base):
    """Dashboard configuration"""

    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    layout = Column(JSON)  # Dashboard layout configuration
    widgets = Column(JSON)  # Widget configurations
    is_public = Column(Boolean, default=False)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Widget(Base):
    """Dashboard widget"""

    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    widget_type = Column(String(50))  # line, bar, pie, table, etc.
    title = Column(String(200))
    config = Column(JSON)  # Widget-specific configuration
    data_query = Column(Text)  # Query to fetch data
    position = Column(JSON)  # Position in dashboard
    created_at = Column(DateTime, default=datetime.utcnow)


class Analysis(Base):
    """Analysis job"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    parameters = Column(JSON)  # Analysis parameters
    results = Column(JSON)  # Analysis results
    accuracy = Column(Float)
    confidence = Column(Float)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="analyses")


class Report(Base):
    """Generated report"""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    report_format = Column(SQLEnum(ReportFormat), nullable=False)
    template = Column(String(200))
    parameters = Column(JSON)
    file_path = Column(String(500))
    file_size = Column(Integer)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    generated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Metric(Base):
    """Metric definition"""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    calculation = Column(Text)  # Metric calculation formula
    unit = Column(String(50))
    target_value = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MetricValue(Base):
    """Metric value over time"""

    __tablename__ = "metric_values"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"))
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    dimensions = Column(JSON)  # Dimensional breakdown
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    """Analytics alert"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    metric_id = Column(Integer, ForeignKey("metrics.id"))
    condition = Column(Text)  # Alert condition
    threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Insight(Base):
    """AI-generated insight"""

    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    insight_type = Column(String(50))  # trend, anomaly, correlation, etc.
    confidence = Column(Float)
    impact = Column(String(20))  # high, medium, low
    data = Column(JSON)  # Supporting data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
