"""
Configuration settings for ProofLink.AI
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "ProofLink.AI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql://prooflink:prooflink123@localhost:5432/prooflink"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-change-this"

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None

    # MCP Configuration
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 8001
    MCP_ENABLE_LOGGING: bool = True

    # Cloud Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: str = "prooflink-proofs"
    AWS_S3_REGION: str = "us-east-1"

    # Google Drive Integration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = (
        "http://localhost:8000/api/v1/integrations/google/callback"
    )

    # Dropbox Integration
    DROPBOX_APP_KEY: Optional[str] = None
    DROPBOX_APP_SECRET: Optional[str] = None

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@prooflink.ai"
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@prooflink.ai"
    SMTP_FROM_NAME: str = "ProofLink.AI"

    # Stripe Payment
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_MONTHLY_PRICE_ID: str = "price_monthly_1usd"
    STRIPE_LIFETIME_PRICE_ID: str = "price_lifetime_5usd"
    STRIPE_YEARLY_PRICE_ID: str = "price_yearly_10usd"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000

    # File Upload
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: str = "pdf,doc,docx,txt,jpg,jpeg,png,gif,mp4,mp3,zip"

    # Proof Configuration
    PROOF_HASH_ALGORITHM: str = "SHA256"
    PROOF_SIGNATURE_ALGORITHM: str = "RSA"
    PROOF_LINK_EXPIRY_DAYS: int = 0  # 0 = never expires
    PROOF_STORAGE_RETENTION_DAYS: int = 365

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"

    # Analytics
    GOOGLE_ANALYTICS_ID: Optional[str] = None
    MIXPANEL_TOKEN: Optional[str] = None

    # CDN
    CDN_URL: str = "https://cdn.prooflink.ai"
    CDN_ENABLED: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/prooflink.log"

    # Feature Flags
    ENABLE_AI_VERIFICATION: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_API_ACCESS: bool = True
    ENABLE_WEBHOOKS: bool = True
    ENABLE_CUSTOM_BRANDING: bool = False

    # Free Tier Limits
    FREE_TIER_PROOFS_PER_MONTH: int = 10
    FREE_TIER_FILE_SIZE_MB: int = 10
    FREE_TIER_API_CALLS_PER_DAY: int = 100

    # Premium Tier Limits
    PREMIUM_TIER_PROOFS_PER_MONTH: str = "unlimited"
    PREMIUM_TIER_FILE_SIZE_MB: int = 100
    PREMIUM_TIER_API_CALLS_PER_DAY: int = 10000

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list"""
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
