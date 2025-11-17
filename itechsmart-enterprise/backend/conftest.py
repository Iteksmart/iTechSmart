"""
iTechSmart Enterprise Test Configuration
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
from app.models.user import User, Tenant
from app.models.ticket import Ticket
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/enterprise_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
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
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create test tenant"""
    tenant = Tenant(
        name="Test Corporation",
        subdomain="testcorp",
        plan="enterprise",
        is_active=True,
        max_users=1000,
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create test user"""
    user = User(
        email="test@testcorp.com",
        full_name="Test User",
        hashed_password=get_password_hash("Test123!"),
        tenant_id=test_tenant.id,
        role="admin",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create test admin user"""
    admin = User(
        email="admin@testcorp.com",
        full_name="Admin User",
        hashed_password=get_password_hash("Admin123!"),
        tenant_id=test_tenant.id,
        role="owner",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user"""
    response = await client.post(
        "/api/v1/auth/login", json={"email": test_user.email, "password": "Test123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client: AsyncClient, test_admin: User) -> dict:
    """Get authentication headers for admin user"""
    response = await client.post(
        "/api/v1/auth/login", json={"email": test_admin.email, "password": "Admin123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_ticket(
    db_session: AsyncSession, test_user: User, test_tenant: Tenant
) -> Ticket:
    """Create test ticket"""
    ticket = Ticket(
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        title="Test Issue",
        description="Test ticket description",
        priority="high",
        status="open",
        category="incident",
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)
    return ticket


# Test data fixtures
@pytest.fixture
def sample_tenant_data() -> dict:
    """Sample tenant data"""
    return {
        "name": "New Enterprise",
        "subdomain": "newenterprise",
        "plan": "enterprise",
        "max_users": 500,
    }


@pytest.fixture
def sample_ticket_data() -> dict:
    """Sample ticket data"""
    return {
        "title": "System Outage",
        "description": "Production system is down",
        "priority": "critical",
        "category": "incident",
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data"""
    return {
        "email": "newuser@testcorp.com",
        "full_name": "New User",
        "password": "NewUser123!",
        "role": "user",
    }


# Cleanup
@pytest.fixture(autouse=True)
async def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here
