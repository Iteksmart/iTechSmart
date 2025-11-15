"""
iTechSmart Connect - Database Configuration
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import redis
from contextlib import contextmanager

# Database URLs
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://connect_user:connect_password@postgres:5432/connect"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "connect_password")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ============================================================================
# POSTGRESQL CONFIGURATION
# ============================================================================

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Database session context manager
    Usage: with get_db_context() as db:
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# ============================================================================
# REDIS UTILITIES
# ============================================================================

class RedisCache:
    """Redis cache utilities"""
    
    @staticmethod
    def get(key: str) -> str:
        """Get value from cache"""
        try:
            return redis_client.get(key)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        try:
            return redis_client.setex(key, expire, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        try:
            return redis_client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    def exists(key: str) -> bool:
        """Check if key exists"""
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    @staticmethod
    def increment(key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            return redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0
    
    @staticmethod
    def expire(key: str, seconds: int) -> bool:
        """Set expiration on key"""
        try:
            return redis_client.expire(key, seconds)
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False

# ============================================================================
# RATE LIMITING UTILITIES
# ============================================================================

class RateLimiter:
    """Rate limiting using Redis"""
    
    @staticmethod
    def check_rate_limit(
        identifier: str,
        limit: int,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded
        Returns: (is_allowed, remaining_requests)
        """
        key = f"rate_limit:{identifier}"
        
        try:
            current = redis_client.get(key)
            
            if current is None:
                # First request in window
                redis_client.setex(key, window_seconds, 1)
                return True, limit - 1
            
            current = int(current)
            
            if current >= limit:
                # Rate limit exceeded
                ttl = redis_client.ttl(key)
                return False, 0
            
            # Increment counter
            new_count = redis_client.incr(key)
            return True, limit - new_count
            
        except Exception as e:
            print(f"Rate limit check error: {e}")
            # Allow request on error
            return True, limit

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all database tables"""
    from models import Base
    Base.metadata.drop_all(bind=engine)

# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_db_health() -> bool:
    """Check if database is healthy"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

def check_redis_health() -> bool:
    """Check if Redis is healthy"""
    try:
        return redis_client.ping()
    except Exception as e:
        print(f"Redis health check failed: {e}")
        return False