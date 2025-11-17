from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
from typing import Generator
import os

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://marketplace_user:marketplace_pass@localhost:5432/marketplace_db",
)

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get Redis client
def get_redis():
    return redis_client


# Cache utilities
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get(self, key: str):
        """Get value from cache"""
        return self.redis.get(key)

    def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache with expiration"""
        return self.redis.setex(key, expire, value)

    def delete(self, key: str):
        """Delete key from cache"""
        return self.redis.delete(key)

    def exists(self, key: str):
        """Check if key exists"""
        return self.redis.exists(key)

    def increment(self, key: str, amount: int = 1):
        """Increment counter"""
        return self.redis.incrby(key, amount)

    def get_hash(self, key: str, field: str):
        """Get hash field value"""
        return self.redis.hget(key, field)

    def set_hash(self, key: str, field: str, value: str):
        """Set hash field value"""
        return self.redis.hset(key, field, value)

    def get_all_hash(self, key: str):
        """Get all hash fields"""
        return self.redis.hgetall(key)

    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            return self.redis.delete(*keys)
        return 0


# Initialize cache manager
cache = CacheManager(redis_client)


# Rate limiting utilities
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if rate limit is exceeded

        Args:
            key: Unique identifier (e.g., user_id, ip_address)
            limit: Maximum number of requests
            window: Time window in seconds

        Returns:
            True if within limit, False if exceeded
        """
        current = self.redis.get(key)

        if current is None:
            # First request in window
            self.redis.setex(key, window, 1)
            return True

        if int(current) < limit:
            # Increment counter
            self.redis.incr(key)
            return True

        # Rate limit exceeded
        return False

    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests in current window"""
        current = self.redis.get(key)
        if current is None:
            return limit
        return max(0, limit - int(current))

    def reset_limit(self, key: str):
        """Reset rate limit for key"""
        return self.redis.delete(key)


# Initialize rate limiter
rate_limiter = RateLimiter(redis_client)


# Session management utilities
class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "session:"

    def create_session(self, user_id: int, token: str, expire: int = 86400):
        """Create user session"""
        key = f"{self.prefix}{token}"
        return self.redis.setex(key, expire, user_id)

    def get_session(self, token: str):
        """Get user session"""
        key = f"{self.prefix}{token}"
        return self.redis.get(key)

    def delete_session(self, token: str):
        """Delete user session"""
        key = f"{self.prefix}{token}"
        return self.redis.delete(key)

    def extend_session(self, token: str, expire: int = 86400):
        """Extend session expiration"""
        key = f"{self.prefix}{token}"
        return self.redis.expire(key, expire)


# Initialize session manager
session_manager = SessionManager(redis_client)


# Analytics tracking utilities
class AnalyticsTracker:
    def __init__(self, redis_client):
        self.redis = redis_client

    def track_view(self, app_id: int):
        """Track app view"""
        key = f"analytics:views:{app_id}"
        return self.redis.incr(key)

    def track_download(self, app_id: int):
        """Track app download"""
        key = f"analytics:downloads:{app_id}"
        return self.redis.incr(key)

    def track_purchase(self, app_id: int, amount: float):
        """Track app purchase"""
        views_key = f"analytics:purchases:{app_id}"
        revenue_key = f"analytics:revenue:{app_id}"
        self.redis.incr(views_key)
        self.redis.incrbyfloat(revenue_key, amount)

    def get_stats(self, app_id: int):
        """Get app statistics"""
        views = self.redis.get(f"analytics:views:{app_id}") or 0
        downloads = self.redis.get(f"analytics:downloads:{app_id}") or 0
        purchases = self.redis.get(f"analytics:purchases:{app_id}") or 0
        revenue = self.redis.get(f"analytics:revenue:{app_id}") or 0.0

        return {
            "views": int(views),
            "downloads": int(downloads),
            "purchases": int(purchases),
            "revenue": float(revenue),
        }


# Initialize analytics tracker
analytics_tracker = AnalyticsTracker(redis_client)
