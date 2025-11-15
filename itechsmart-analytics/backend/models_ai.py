"""
iTechSmart Analytics - AI Insights Models
AI-powered predictive analytics and intelligent insights
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class ModelType(enum.Enum):
    """Types of AI models"""
    TIME_SERIES = "time_series"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    FORECASTING = "forecasting"


class ModelStatus(enum.Enum):
    """Status of AI models"""
    DRAFT = "draft"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"


class PredictionStatus(enum.Enum):
    """Status of predictions"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class InsightType(enum.Enum):
    """Types of insights"""
    ANOMALY = "anomaly"
    TREND = "trend"
    PATTERN = "pattern"
    CORRELATION = "correlation"
    FORECAST = "forecast"
    RECOMMENDATION = "recommendation"


class InsightSeverity(enum.Enum):
    """Severity levels for insights"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationType(enum.Enum):
    """Types of recommendations"""
    OPTIMIZATION = "optimization"
    COST_SAVING = "cost_saving"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CAPACITY = "capacity"
    MAINTENANCE = "maintenance"


class AIModel(Base):
    """AI/ML model for predictions and insights"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    model_type = Column(Enum(ModelType), nullable=False)
    status = Column(Enum(ModelStatus), default=ModelStatus.DRAFT)
    
    # Model configuration
    algorithm = Column(String(100))  # e.g., "ARIMA", "Prophet", "RandomForest"
    hyperparameters = Column(JSON)  # Model-specific parameters
    features = Column(JSON)  # List of feature columns
    target_variable = Column(String(100))  # What we're predicting
    
    # Training data
    training_data_source = Column(String(200))  # Dataset or query
    training_start_date = Column(DateTime)
    training_end_date = Column(DateTime)
    training_samples = Column(Integer)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    rmse = Column(Float)  # Root Mean Square Error
    mae = Column(Float)   # Mean Absolute Error
    r2_score = Column(Float)  # R-squared
    
    # Model artifacts
    model_path = Column(String(500))  # Path to saved model file
    model_version = Column(String(50))
    model_size_mb = Column(Float)
    
    # Deployment
    is_deployed = Column(Boolean, default=False)
    deployment_date = Column(DateTime)
    endpoint_url = Column(String(500))
    
    # Metadata
    created_by = Column(Integer)  # User ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trained_at = Column(DateTime)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="model", cascade="all, delete-orphan")


class Prediction(Base):
    """Prediction made by an AI model"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    
    # Prediction details
    prediction_type = Column(String(100))  # e.g., "forecast", "classification"
    input_data = Column(JSON)  # Input features
    predicted_value = Column(JSON)  # Predicted output (can be numeric, categorical, etc.)
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    # Time-series specific
    prediction_date = Column(DateTime)  # When prediction is for
    prediction_horizon = Column(Integer)  # How far ahead (in time units)
    
    # Confidence intervals (for regression/forecasting)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    confidence_level = Column(Float)  # e.g., 0.95 for 95% confidence
    
    # Actual vs predicted (for validation)
    actual_value = Column(JSON)
    prediction_error = Column(Float)
    
    # Status and metadata
    status = Column(Enum(PredictionStatus), default=PredictionStatus.PENDING)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    
    # Relationships
    model = relationship("AIModel", back_populates="predictions")


class Insight(Base):
    """AI-generated insight or finding"""
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    
    # Insight details
    insight_type = Column(Enum(InsightType), nullable=False)
    severity = Column(Enum(InsightSeverity), default=InsightSeverity.INFO)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Data and analysis
    affected_metrics = Column(JSON)  # List of metrics involved
    data_points = Column(JSON)  # Supporting data
    statistical_significance = Column(Float)  # p-value or confidence
    
    # Anomaly detection specific
    anomaly_score = Column(Float)
    expected_value = Column(Float)
    actual_value = Column(Float)
    deviation_percentage = Column(Float)
    
    # Trend analysis specific
    trend_direction = Column(String(50))  # "increasing", "decreasing", "stable"
    trend_strength = Column(Float)  # 0.0 to 1.0
    trend_duration_days = Column(Integer)
    
    # Pattern recognition
    pattern_type = Column(String(100))  # e.g., "seasonal", "cyclical", "irregular"
    pattern_frequency = Column(String(50))  # e.g., "daily", "weekly", "monthly"
    
    # Time context
    detection_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Actions and status
    is_actionable = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer)  # User ID
    acknowledged_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When insight is no longer relevant
    
    # Relationships
    model = relationship("AIModel", back_populates="insights")
    recommendations = relationship("Recommendation", back_populates="insight", cascade="all, delete-orphan")


class Recommendation(Base):
    """AI-generated recommendation for action"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    insight_id = Column(Integer, ForeignKey("insights.id"))
    
    # Recommendation details
    recommendation_type = Column(Enum(RecommendationType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    rationale = Column(Text)  # Why this recommendation
    
    # Impact analysis
    expected_impact = Column(Text)
    estimated_cost_savings = Column(Float)
    estimated_performance_gain = Column(Float)
    risk_level = Column(String(50))  # "low", "medium", "high"
    
    # Implementation
    implementation_steps = Column(JSON)  # List of steps
    estimated_effort_hours = Column(Float)
    required_resources = Column(JSON)  # List of resources needed
    
    # Priority and urgency
    priority = Column(Integer)  # 1-5, 1 being highest
    urgency = Column(String(50))  # "immediate", "short_term", "long_term"
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, accepted, rejected, implemented
    accepted_by = Column(Integer)  # User ID
    accepted_at = Column(DateTime)
    implemented_at = Column(DateTime)
    
    # Results tracking
    actual_impact = Column(Text)
    actual_cost_savings = Column(Float)
    actual_performance_gain = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    insight = relationship("Insight", back_populates="recommendations")


class DataQualityScore(Base):
    """AI-assessed data quality metrics"""
    __tablename__ = "data_quality_scores"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Data source
    dataset_name = Column(String(200), nullable=False)
    table_name = Column(String(200))
    column_name = Column(String(200))
    
    # Quality dimensions
    completeness_score = Column(Float)  # % of non-null values
    accuracy_score = Column(Float)  # Based on validation rules
    consistency_score = Column(Float)  # Cross-field consistency
    timeliness_score = Column(Float)  # Data freshness
    validity_score = Column(Float)  # Format and type validity
    uniqueness_score = Column(Float)  # Duplicate detection
    
    # Overall score
    overall_score = Column(Float)  # Weighted average
    
    # Issues detected
    missing_values_count = Column(Integer)
    duplicate_count = Column(Integer)
    outlier_count = Column(Integer)
    invalid_format_count = Column(Integer)
    
    # Recommendations
    quality_issues = Column(JSON)  # List of specific issues
    improvement_suggestions = Column(JSON)
    
    # Metadata
    assessed_at = Column(DateTime, default=datetime.utcnow)
    sample_size = Column(Integer)
    total_records = Column(Integer)


class FeatureImportance(Base):
    """Feature importance scores for ML models"""
    __tablename__ = "feature_importance"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    
    # Feature details
    feature_name = Column(String(200), nullable=False)
    importance_score = Column(Float, nullable=False)  # 0.0 to 1.0
    importance_rank = Column(Integer)
    
    # Statistical measures
    correlation_with_target = Column(Float)
    p_value = Column(Float)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)


class ModelExperiment(Base):
    """Track ML model experiments and hyperparameter tuning"""
    __tablename__ = "model_experiments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    
    # Experiment details
    experiment_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Configuration
    algorithm = Column(String(100))
    hyperparameters = Column(JSON)
    features_used = Column(JSON)
    
    # Results
    training_score = Column(Float)
    validation_score = Column(Float)
    test_score = Column(Float)
    cross_validation_scores = Column(JSON)
    
    # Performance metrics
    metrics = Column(JSON)  # All performance metrics
    
    # Training details
    training_time_seconds = Column(Float)
    training_samples = Column(Integer)
    
    # Status
    status = Column(String(50), default="running")
    error_message = Column(Text)
    
    # Metadata
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class AutoMLRun(Base):
    """Automated machine learning run"""
    __tablename__ = "automl_runs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Run details
    run_name = Column(String(200), nullable=False)
    objective = Column(String(100))  # e.g., "maximize_accuracy", "minimize_rmse"
    
    # Configuration
    algorithms_tested = Column(JSON)  # List of algorithms
    max_trials = Column(Integer)
    max_time_minutes = Column(Integer)
    
    # Results
    best_model_id = Column(Integer, ForeignKey("ai_models.id"))
    best_score = Column(Float)
    trials_completed = Column(Integer)
    
    # All trials
    trial_results = Column(JSON)  # List of all trial results
    
    # Status
    status = Column(String(50), default="running")
    progress_percentage = Column(Float)
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(Integer)