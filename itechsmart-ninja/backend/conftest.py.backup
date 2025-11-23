"""
iTechSmart Ninja Test Configuration
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
from app.models.user import User
from app.models.agent import Agent
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/ninja_test"

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
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("Test123!"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """Create test admin user"""
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("Admin123!"),
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
async def test_agent(db_session: AsyncSession, test_user: User) -> Agent:
    """Create test AI agent"""
    agent = Agent(
        user_id=test_user.id,
        name="Test Agent",
        description="Test AI agent",
        agent_type="automation",
        status="active",
        capabilities=["task_execution", "monitoring"],
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


# Test data fixtures
@pytest.fixture
def sample_agent_data() -> dict:
    """Sample agent creation data"""
    return {
        "name": "Monitoring Agent",
        "description": "System monitoring agent",
        "agent_type": "monitoring",
        "capabilities": ["system_monitoring", "alerting"],
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data"""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "NewUser123!",
    }


# Cleanup
@pytest.fixture(autouse=True)
async def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here
