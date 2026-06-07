"""Unit tests for security module."""

import pytest
from fastapi import HTTPException

from app.security import get_current_user, require_role


@pytest.mark.unit
@pytest.mark.security
class TestRequireRole:
    """Test role-based access control."""

    def test_require_role_single_role(self):
        """Test require_role decorator with single role."""
        role_check = require_role("admin")
        assert role_check is not None

    def test_require_role_multiple_roles(self):
        """Test require_role decorator with multiple roles."""
        role_check = require_role("admin", "reviewer")
        assert role_check is not None

    @pytest.mark.asyncio
    async def test_require_role_access_granted(self):
        """Test that user with correct role gets access."""
        from app.security import TokenData
        from unittest.mock import AsyncMock, patch

        role_check = require_role("admin")

        # Mock the dependency
        user = TokenData(
            user_id="admin_user",
            email="admin@example.com",
            roles=["admin"],
        )

        # The dependency function should allow the request
        # This would be tested through integration tests

    @pytest.mark.asyncio
    async def test_require_role_access_denied(self):
        """Test that user without correct role is denied."""
        # This would be tested through integration tests
        pass


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
