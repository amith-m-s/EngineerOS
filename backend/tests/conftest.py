"""Pytest configuration and shared fixtures."""

import asyncio
import os
from typing import Generator

import pytest
from faker import Faker
from fastapi.testclient import TestClient

# Set test environment — must be before any app imports
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-12345-never-use-in-production"
os.environ["POSTGRES_DSN"] = "sqlite:///./test.db"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "testpassword"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"

from app.config import get_settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client with lifespan context."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def faker():
    """Faker instance for generating test data."""
    return Faker()


@pytest.fixture
def settings():
    """Application settings."""
    return get_settings()


@pytest.fixture
def valid_jwt_token(settings) -> str:
    """Generate a valid JWT token for testing."""
    from app.auth import create_access_token

    token_response = create_access_token(
        user_id="test_user",
        email="test@engineeros.io",
        roles=["engineer"],
    )
    return token_response.access_token


@pytest.fixture
def admin_jwt_token(settings) -> str:
    """Generate an admin JWT token for testing."""
    from app.auth import create_access_token

    token_response = create_access_token(
        user_id="admin_user",
        email="admin@engineeros.io",
        roles=["admin"],
    )
    return token_response.access_token


@pytest.fixture
def auth_headers(valid_jwt_token: str) -> dict:
    """Authorization headers with valid JWT token."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def admin_auth_headers(admin_jwt_token: str) -> dict:
    """Authorization headers with admin JWT token."""
    return {"Authorization": f"Bearer {admin_jwt_token}"}


class AuthTestData:
    """Test data for authentication tests."""

    valid_email = "test@engineeros.io"
    valid_password = "ValidPassword123!"
    valid_user_id = "test_user_123"
    valid_full_name = "Test Engineer"

    demo_email = "demo@engineeros.io"
    demo_password = "demo1234"
    demo_user_id = "demo_user"

    invalid_email = "not-an-email"
    invalid_password = "short"  # Less than 8 chars
    missing_email = None
    missing_password = None


@pytest.fixture
def auth_test_data():
    """Test data for authentication."""
    return AuthTestData()
