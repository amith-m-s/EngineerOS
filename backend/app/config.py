"""Configuration management for EngineerOS."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: Literal["development", "staging", "production", "testing"] = "development"
    debug: bool = False

    # Security
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""

    # Database — development defaults use SQLite so the app runs without Docker
    postgres_dsn: str = "sqlite:///./engineeros_dev.db"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    # API
    api_title: str = "EngineerOS API"
    api_version: str = "0.1.0"
    api_cors_origins: str = "http://localhost:3000,http://localhost:3001"
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    # Observability
    sentry_dsn: str = ""
    log_level: str = "INFO"
    prometheus_enabled: bool = True
    otlp_enabled: bool = False
    otlp_endpoint: str = "http://localhost:4317"
    jaeger_enabled: bool = False
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831
    jaeger_sampler: str = "const"  # const, probabilistic, rate_limiting
    jaeger_sampler_param: float = 1.0  # Full sampling for development

    class Config:
        """Pydantic settings configuration."""
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite backend (development fallback)."""
        return self.postgres_dsn.startswith("sqlite")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
