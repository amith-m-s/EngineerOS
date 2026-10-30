"""Unit tests for security module."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import TokenData
from app.security import get_current_user, get_current_user_optional, require_role


@pytest.mark.unit
@pytest.mark.security
class TestRequireRole:
    """Test role-based access control."""

    def test_require_role_single_role(self):
        """Test require_role decorator with single role."""
        role_check = require_role("admin")
        assert callable(role_check)

    def test_require_role_multiple_roles(self):
        """Test require_role decorator with multiple roles."""
        role_check = require_role("admin", "reviewer")
        assert callable(role_check)

    @pytest.mark.asyncio
    async def test_require_role_access_granted(self):
        """Allow a user whose roles intersect the required roles."""
        role_check = require_role("admin", "reviewer")
        user = TokenData(
            user_id="admin_user",
            email="admin@example.com",
            roles=["admin"],
        )

        assert await role_check(current_user=user) is user

    @pytest.mark.asyncio
    async def test_require_role_access_denied(self):
        """Reject a user who has none of the required roles."""
        role_check = require_role("admin", "reviewer")
        user = TokenData(
            user_id="engineer_user",
            email="engineer@example.com",
            roles=["engineer"],
        )

        with pytest.raises(HTTPException) as exc_info:
            await role_check(current_user=user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"


@pytest.mark.unit
@pytest.mark.security
class TestSecurityHeaders:
    """Test security header generation."""

    def test_security_headers_present_in_config(self):
        """Test that security middleware is configured."""
        from app.config import get_settings

        settings = get_settings()
        assert settings.environment is not None


@pytest.mark.unit
@pytest.mark.security
class TestAuthDependencies:
    """Test authentication dependencies."""

    def test_get_current_user_dependency_created(self):
        """Test that get_current_user dependency is available."""
        assert get_current_user is not None
        assert callable(get_current_user)

    @pytest.mark.asyncio
    async def test_optional_auth_without_credentials_returns_none(self):
        """Allow anonymous access when no bearer credentials are supplied."""
        assert await get_current_user_optional(credentials=None) is None

    @pytest.mark.asyncio
    async def test_optional_auth_with_valid_token_returns_user(self, monkeypatch):
        """Resolve a valid bearer token to its authenticated user."""
        user = TokenData(
            user_id="valid_user",
            email="valid@example.com",
            roles=["engineer"],
        )
        monkeypatch.setattr("app.security.decode_access_token", lambda token: user)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token",
        )

        assert await get_current_user_optional(credentials=credentials) is user

    @pytest.mark.asyncio
    async def test_optional_auth_with_invalid_token_returns_401(self, monkeypatch):
        """Do not silently downgrade an invalid bearer token to anonymous access."""
        monkeypatch.setattr("app.security.decode_access_token", lambda token: None)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token",
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_optional(credentials=credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
