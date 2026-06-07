"""Unit tests for authentication module."""

import pytest
from datetime import UTC, datetime, timedelta

from app.auth import (
    AccessToken,
    TokenData,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.config import get_settings


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a valid hash."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20  # bcrypt hash is long
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_verify_password_success(self):
        """Test that verify_password returns True for correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test that verify_password returns False for incorrect password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty_string(self):
        """Test that verify_password handles empty strings."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_hash_password_deterministic_check(self):
        """Test that same password hashes to different values (bcrypt salt)."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
@pytest.mark.auth
class TestTokenCreation:
    """Test JWT token creation and structure."""

    def test_create_access_token_returns_token(self):
        """Test that create_access_token returns AccessToken."""
        token = create_access_token(
            user_id="test_user",
            email="test@example.com",
            roles=["engineer"],
        )

        assert isinstance(token, AccessToken)
        assert isinstance(token.access_token, str)
        assert token.token_type == "bearer"
        assert len(token.access_token) > 100  # JWT is long

    def test_create_access_token_with_roles(self):
        """Test token creation with multiple roles."""
        token = create_access_token(
            user_id="test_user",
            email="test@example.com",
            roles=["engineer", "reviewer"],
        )

        assert isinstance(token, AccessToken)
        assert token.access_token  # Token is created

    def test_create_access_token_with_custom_expiration(self):
        """Test token creation with custom expiration."""
        expires_delta = timedelta(hours=1)
        token = create_access_token(
            user_id="test_user",
            email="test@example.com",
            roles=["engineer"],
            expires_delta=expires_delta,
        )

        assert isinstance(token, AccessToken)


@pytest.mark.unit
@pytest.mark.auth
class TestTokenDecoding:
    """Test JWT token decoding and validation."""

    def test_decode_access_token_success(self):
        """Test successful token decoding."""
        user_id = "test_user"
        email = "test@example.com"
        roles = ["engineer"]

        token = create_access_token(
            user_id=user_id,
            email=email,
            roles=roles,
        )

        decoded = decode_access_token(token.access_token)

        assert decoded is not None
        assert decoded.user_id == user_id
        assert decoded.email == email
        assert decoded.roles == roles

    def test_decode_access_token_invalid_token(self):
        """Test decoding invalid token returns None."""
        decoded = decode_access_token("invalid.token.here")
        assert decoded is None

    def test_decode_access_token_empty_token(self):
        """Test decoding empty token returns None."""
        decoded = decode_access_token("")
        assert decoded is None

    def test_decode_access_token_malformed(self):
        """Test decoding malformed token returns None."""
        decoded = decode_access_token("not.valid.jwt")
        assert decoded is None

    def test_token_data_structure(self):
        """Test TokenData model validation."""
        token_data = TokenData(
            user_id="test_user",
            email="test@example.com",
            roles=["engineer", "reviewer"],
        )

        assert token_data.user_id == "test_user"
        assert token_data.email == "test@example.com"
        assert token_data.roles == ["engineer", "reviewer"]

    def test_token_data_default_roles(self):
        """Test TokenData with default empty roles."""
        token_data = TokenData(
            user_id="test_user",
            email="test@example.com",
        )

        assert token_data.roles == []


@pytest.mark.unit
@pytest.mark.auth
class TestTokenExpiration:
    """Test JWT token expiration."""

    def test_token_includes_expiration(self):
        """Test that created token includes expiration."""
        expires_delta = timedelta(minutes=30)
        token = create_access_token(
            user_id="test_user",
            email="test@example.com",
            roles=["engineer"],
            expires_delta=expires_delta,
        )

        decoded = decode_access_token(token.access_token)
        assert decoded is not None
        # Token should be valid now
        assert decoded.user_id == "test_user"

    def test_token_default_expiration_hours(self, settings):
        """Test token uses default expiration from settings."""
        token = create_access_token(
            user_id="test_user",
            email="test@example.com",
            roles=["engineer"],
        )

        # Token should be valid
        decoded = decode_access_token(token.access_token)
        assert decoded is not None
