"""
iTechSmart HL7 Test Configuration
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
from app.models.patient import Patient
from app.models.hl7_message import HL7Message
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/hl7_test"

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
        email="test@hospital.com",
        full_name="Test User",
        hashed_password=get_password_hash("Test123!"),
        role="clinician",
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
        email="admin@hospital.com",
        full_name="Admin User",
        hashed_password=get_password_hash("Admin123!"),
        role="admin",
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
async def test_patient(db_session: AsyncSession) -> Patient:
    """Create test patient"""
    patient = Patient(
        mrn="MRN123456",
        first_name="John",
        last_name="Doe",
        date_of_birth="1980-01-01",
        gender="M",
        ssn="123-45-6789",
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
async def test_hl7_message(
    db_session: AsyncSession, test_patient: Patient
) -> HL7Message:
    """Create test HL7 message"""
    message = HL7Message(
        patient_id=test_patient.id,
        message_type="ADT^A01",
        raw_message="MSH|^~\\&|EPIC|HOSPITAL|||20240101120000||ADT^A01|MSG123|P|2.5",
        status="processed",
        source_system="EPIC",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


# Test data fixtures
@pytest.fixture
def sample_hl7_adt_message() -> str:
    """Sample HL7 ADT message"""
    return """MSH|^~\\&|EPIC|HOSPITAL|||20240101120000||ADT^A01|MSG123|P|2.5
EVN|A01|20240101120000
PID|1||MRN123456||DOE^JOHN||19800101|M|||123 MAIN ST^^CITY^ST^12345||555-1234|||M|NON|123456789
PV1|1|I|ICU^101^01||||DOC123^SMITH^JOHN|||MED||||1|||DOC123^SMITH^JOHN||VIS123|||||||||||||||||||||||||20240101120000"""


@pytest.fixture
def sample_fhir_patient() -> dict:
    """Sample FHIR patient resource"""
    return {
        "resourceType": "Patient",
        "id": "example",
        "identifier": [{"system": "http://hospital.com/mrn", "value": "MRN123456"}],
        "name": [{"family": "Doe", "given": ["John"]}],
        "gender": "male",
        "birthDate": "1980-01-01",
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data"""
    return {
        "email": "newuser@hospital.com",
        "full_name": "New User",
        "password": "NewUser123!",
        "role": "clinician",
    }


# Cleanup
@pytest.fixture(autouse=True)
async def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here
