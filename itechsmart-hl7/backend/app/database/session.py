"""
Database Session Management
SQLAlchemy session and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://itechsmart:itechsmart123@localhost:5432/itechsmart_hl7"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False,          # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
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
    from .models import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_db():
    """
    Drop all database tables (use with caution!)
    """
    from .models import Base
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


class DatabaseManager:
    """
    Database management utilities
    """
    
    @staticmethod
    def get_session() -> Session:
        """
        Get a new database session
        """
        return SessionLocal()
    
    @staticmethod
    def close_session(session: Session):
        """
        Close database session
        """
        session.close()
    
    @staticmethod
    def commit_session(session: Session):
        """
        Commit database session
        """
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to commit session: {e}")
            raise
    
    @staticmethod
    def rollback_session(session: Session):
        """
        Rollback database session
        """
        session.rollback()
    
    @staticmethod
    def get_table_count(session: Session, model) -> int:
        """
        Get count of records in table
        """
        return session.query(model).count()
    
    @staticmethod
    def truncate_table(session: Session, model):
        """
        Truncate table (delete all records)
        """
        try:
            session.query(model).delete()
            session.commit()
            logger.info(f"Table {model.__tablename__} truncated")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to truncate table: {e}")
            raise


# Database health check
def get_db_health() -> dict:
    """
    Get database health status
    """
    health = {
        "status": "unknown",
        "connection": False,
        "pool_size": 0,
        "pool_overflow": 0,
        "pool_checked_out": 0
    }
    
    try:
        # Check connection
        health["connection"] = check_db_connection()
        
        # Get pool statistics
        pool = engine.pool
        health["pool_size"] = pool.size()
        health["pool_overflow"] = pool.overflow()
        health["pool_checked_out"] = pool.checkedout()
        
        health["status"] = "healthy" if health["connection"] else "unhealthy"
        
    except Exception as e:
        logger.error(f"Failed to get database health: {e}")
        health["status"] = "error"
        health["error"] = str(e)
    
    return health