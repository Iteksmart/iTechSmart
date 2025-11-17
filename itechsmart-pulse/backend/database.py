"""
iTechSmart Pulse - Database Configuration
SQLAlchemy Database Setup
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from typing import Generator

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://pulse_user:pulse_pass_2024@localhost:5432/pulse_db"
)

# ClickHouse URL for analytics
CLICKHOUSE_URL = os.getenv(
    "CLICKHOUSE_URL", "clickhouse://default:@localhost:9000/analytics"
)

# Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    """
    from models import Base

    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables - use with caution!
    """
    from models import Base

    Base.metadata.drop_all(bind=engine)


# ============================================================================
# CLICKHOUSE CONNECTION
# ============================================================================

from clickhouse_driver import Client as ClickHouseClient


def get_clickhouse_client():
    """
    Get ClickHouse client for analytics queries
    """
    return ClickHouseClient(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "9000")),
        database=os.getenv("CLICKHOUSE_DB", "analytics"),
        user=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
    )


# ============================================================================
# REDIS CONNECTION
# ============================================================================

import redis
from typing import Optional


class RedisCache:
    """Redis cache manager"""

    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        return self.redis_client.get(key)

    def set(self, key: str, value: str, ttl: int = 300):
        """Set value in cache with TTL"""
        self.redis_client.setex(key, ttl, value)

    def delete(self, key: str):
        """Delete key from cache"""
        self.redis_client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.redis_client.exists(key)

    def flush_all(self):
        """Flush all cache - use with caution!"""
        self.redis_client.flushall()


# Global cache instance
cache = RedisCache()


# ============================================================================
# DATABASE UTILITIES
# ============================================================================


def execute_query(query: str, params: dict = None):
    """
    Execute a raw SQL query
    """
    db = SessionLocal()
    try:
        result = db.execute(query, params or {})
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def execute_clickhouse_query(query: str):
    """
    Execute a ClickHouse analytics query
    """
    client = get_clickhouse_client()
    try:
        result = client.execute(query)
        return result
    except Exception as e:
        raise e


# ============================================================================
# CONNECTION TESTING
# ============================================================================


def test_postgresql_connection() -> bool:
    """Test PostgreSQL connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return False


def test_clickhouse_connection() -> bool:
    """Test ClickHouse connection"""
    try:
        client = get_clickhouse_client()
        client.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"ClickHouse connection failed: {e}")
        return False


def test_redis_connection() -> bool:
    """Test Redis connection"""
    try:
        cache.redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False


def test_all_connections():
    """Test all database connections"""
    results = {
        "postgresql": test_postgresql_connection(),
        "clickhouse": test_clickhouse_connection(),
        "redis": test_redis_connection(),
    }
    return results
