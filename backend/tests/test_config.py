"""Unit tests for configuration module."""

import pytest
from app.config import Settings, get_settings


@pytest.mark.unit
class TestSettings:
    """Test configuration management."""

    def test_get_settings_returns_settings(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_settings_environment_variable(self):
        """Test that settings loads from environment."""
        settings = get_settings()
        assert settings.environment in ["development", "staging", "production", "testing"]

    def test_settings_has_jwt_config(self):
        """Test that settings has JWT configuration."""
        settings = get_settings()
        assert settings.jwt_secret_key
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_expiration_hours > 0

    def test_settings_has_database_config(self):
        """Test that settings has database configuration."""
        settings = get_settings()
        assert settings.postgres_dsn

    def test_settings_cors_origins_list(self):
        """Test CORS origins parsing."""
        settings = get_settings()
        origins = settings.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) > 0

    def test_settings_rate_limiting_config(self):
        """Test rate limiting configuration."""
        settings = get_settings()
        assert settings.rate_limit_requests > 0
        assert settings.rate_limit_period > 0
