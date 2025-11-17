"""
Configuration management for DataFlow
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "iTechSmart DataFlow"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://dataflow.itechsmart.dev",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://dataflow:password@localhost:5432/dataflow"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "dataflow"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["localhost:9092"]
    KAFKA_CONSUMER_GROUP: str = "dataflow-consumers"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Storage
    S3_BUCKET: str = "dataflow-storage"
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # MinIO (S3-compatible)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "dataflow"

    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Passport Integration
    PASSPORT_API_URL: str = "http://localhost:8001/api/v1"
    PASSPORT_API_KEY: Optional[str] = None

    # Enterprise Hub Integration
    ENTERPRISE_HUB_URL: str = "http://localhost:8002/api/v1"
    ENTERPRISE_HUB_API_KEY: Optional[str] = None

    # Ninja Integration
    NINJA_API_URL: str = "http://localhost:8003/api/v1"
    NINJA_API_KEY: Optional[str] = None

    # ImpactOS Integration
    IMPACTOS_API_URL: str = "http://localhost:8004/api/v1"
    IMPACTOS_API_KEY: Optional[str] = None

    # HL7 Integration
    HL7_API_URL: str = "http://localhost:8005/api/v1"
    HL7_API_KEY: Optional[str] = None

    # Pipeline Settings
    MAX_CONCURRENT_PIPELINES: int = 10
    PIPELINE_TIMEOUT_SECONDS: int = 3600
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 60

    # Data Quality
    ENABLE_DATA_QUALITY: bool = True
    QUALITY_CHECK_SAMPLE_SIZE: int = 1000

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
