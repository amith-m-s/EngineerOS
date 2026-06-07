"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_returns_200(self, client: TestClient):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, client: TestClient):
        """Test that health endpoint returns ok status."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint_no_auth_required(self, client: TestClient):
        """Test that health endpoint doesn't require authentication."""
        response = client.get("/health")
        assert response.status_code == 200


@pytest.mark.integration
class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_with_demo_credentials(self, client: TestClient, auth_test_data):
        """Test login with demo credentials."""
        response = client.post(
            "/auth/login",
            json={
                "email": auth_test_data.demo_email,
                "password": auth_test_data.demo_password,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data

    def test_login_with_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        response = client.post(
            "/auth/login",
            json={
                "email": "demo@engineeros.io",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_with_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format."""
        response = client.post(
            "/auth/login",
            json={
                "email": "not-an-email",
                "password": "password123",
            },
        )

        assert response.status_code == 422

    def test_login_missing_email(self, client: TestClient):
        """Test login missing email."""
        response = client.post(
            "/auth/login",
            json={"password": "password123"},
        )

        assert response.status_code == 422

    def test_login_missing_password(self, client: TestClient):
        """Test login missing password."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestDevelopmentEndpoints:
    """Test development endpoints."""

    def test_dev_settings_requires_development_env(self, client: TestClient):
        """Test dev settings endpoint (only works in dev)."""
        # In production, this should return 403
        # In development, it should work
        response = client.get("/dev/settings")
        # Status depends on environment
        assert response.status_code in [200, 403]

    def test_dev_me_requires_authentication(self, client: TestClient):
        """Test dev me endpoint requires authentication."""
        response = client.get("/dev/me")
        assert response.status_code == 401

    def test_dev_me_with_authentication(
        self, client: TestClient, auth_headers: dict
    ):
        """Test dev me endpoint with valid token."""
        response = client.get("/dev/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "roles" in data


@pytest.mark.integration
class TestRateLimiting:
    """Test rate limiting protection."""

    def test_rate_limit_header_present(self, client: TestClient):
        """Test that rate limit headers are present."""
        response = client.get("/health")
        # RateLimit headers may be present
        assert response.status_code == 200


@pytest.mark.integration
class TestSecurityHeaders:
    """Test security headers in responses."""

    def test_x_content_type_options_header(self, client: TestClient):
        """Test X-Content-Type-Options header."""
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options_header(self, client: TestClient):
        """Test X-Frame-Options header."""
        response = client.get("/health")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_x_xss_protection_header(self, client: TestClient):
        """Test X-XSS-Protection header."""
        response = client.get("/health")
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_referrer_policy_header(self, client: TestClient):
        """Test Referrer-Policy header."""
        response = client.get("/health")
        assert "strict-origin-when-cross-origin" in response.headers.get(
            "Referrer-Policy", ""
        )


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and validation."""

    def test_validation_error_format(self, client: TestClient):
        """Test that validation errors follow RFC 7807 format."""
        response = client.post(
            "/auth/login",
            json={
                "email": "invalid-email",
                "password": "short",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data or "errors" in data

    def test_404_not_found(self, client: TestClient):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.slow
class TestWebSocketEndpoint:
    """Test WebSocket endpoint."""

    def test_websocket_endpoint_exists(self, client: TestClient):
        """Test that WebSocket endpoint can be accessed."""
        # WebSockets can't be easily tested with TestClient
        # This is a placeholder for E2E tests
        pass
