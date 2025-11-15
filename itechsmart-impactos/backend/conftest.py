"""
iTechSmart ImpactOS Test Configuration
Pytest fixtures and configuration for all tests
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings
from app.models.user import User, Organization
from app.models.program import Program
from app.models.grant import Grant
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/impactos_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """Create test organization"""
    org = Organization(
        name="Test Nonprofit",
        ein="12-3456789",
        mission="Help communities",
        website="https://test.org",
        is_active=True
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("Test123!"),
        organization_id=test_organization.id,
        role="admin",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test admin user"""
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=get_password_hash("Admin123!"),
        organization_id=test_organization.id,
        role="owner",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "Test123!"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client: AsyncClient, test_admin: User) -> dict:
    """Get authentication headers for admin user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_admin.email,
            "password": "Admin123!"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_program(db_session: AsyncSession, test_organization: Organization) -> Program:
    """Create test program"""
    program = Program(
        organization_id=test_organization.id,
        name="Youth Education Program",
        description="Educational support for youth",
        category="education",
        status="active",
        start_date="2024-01-01",
        budget=50000
    )
    db_session.add(program)
    await db_session.commit()
    await db_session.refresh(program)
    return program


@pytest.fixture
async def test_grant(db_session: AsyncSession) -> Grant:
    """Create test grant"""
    grant = Grant(
        title="Community Development Grant",
        funder="Test Foundation",
        amount=100000,
        deadline="2024-12-31",
        category="community",
        eligibility="Nonprofits serving communities",
        url="https://grants.example.com/123"
    )
    db_session.add(grant)
    await db_session.commit()
    await db_session.refresh(grant)
    return grant


# Test data fixtures
@pytest.fixture
def sample_organization_data() -> dict:
    """Sample organization data"""
    return {
        "name": "New Nonprofit",
        "ein": "98-7654321",
        "mission": "Serve the community",
        "website": "https://newnpo.org"
    }


@pytest.fixture
def sample_program_data() -> dict:
    """Sample program data"""
    return {
        "name": "Health Initiative",
        "description": "Community health program",
        "category": "health",
        "budget": 75000,
        "start_date": "2024-06-01"
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data"""
    return {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "NewUser123!",
        "organization_name": "User's Nonprofit"
    }


# Cleanup
@pytest.fixture(autouse=True)
async def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here