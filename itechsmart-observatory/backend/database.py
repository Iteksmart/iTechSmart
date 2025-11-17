"""
iTechSmart Observatory - Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://observatory:observatory@localhost:5432/observatory"
)

# Create engine
engine = create_engine(DATABASE_URL, poolclass=StaticPool, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    """
    from .models import Base

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def drop_db():
    """
    Drop all database tables (use with caution!)
    """
    from .models import Base

    Base.metadata.drop_all(bind=engine)
    print("⚠️  Database tables dropped")


if __name__ == "__main__":
    init_db()
