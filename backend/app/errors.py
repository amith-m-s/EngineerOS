"""Error response models following RFC 7807 Problem Details."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs."""

    type: str = Field(
        default="about:blank",
        description="URI identifying the problem type",
    )
    title: str = Field(description="Short human-readable summary")
    status: int = Field(description="HTTP status code")
    detail: str | None = Field(default=None, description="Detailed explanation")
    instance: str | None = Field(default=None, description="URI of the problem instance")
    
    # EngineerOS specific extensions
    error_code: str | None = Field(default=None, description="Internal error code")
    trace_id: str | None = Field(default=None, description="Request trace ID")
    timestamp: str | None = Field(default=None, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "https://api.engineeros.io/errors/invalid-credentials",
                "title": "Invalid Credentials",
                "status": 401,
                "detail": "Email or password is incorrect",
                "error_code": "AUTH_001",
                "trace_id": "abc-123-def-456",
                "timestamp": "2026-06-02T10:30:00Z",
            }
        }


class ValidationErrorDetail(ErrorDetail):
    """RFC 7807 with validation error details."""

    errors: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Field-level validation errors",
    )


# Error code registry
ERROR_CODES = {
    # Authentication errors (4xx)
    "AUTH_001": {
        "status": 401,
        "title": "Invalid Credentials",
        "type": "https://api.engineeros.io/errors/invalid-credentials",
    },
    "AUTH_002": {
        "status": 401,
        "title": "Token Expired",
        "type": "https://api.engineeros.io/errors/token-expired",
    },
    "AUTH_003": {
        "status": 401,
        "title": "Token Invalid",
        "type": "https://api.engineeros.io/errors/token-invalid",
    },
    "AUTH_004": {
        "status": 403,
        "title": "Insufficient Permissions",
        "type": "https://api.engineeros.io/errors/insufficient-permissions",
    },
    
    # Resource errors (4xx)
    "RESOURCE_001": {
        "status": 404,
        "title": "Resource Not Found",
        "type": "https://api.engineeros.io/errors/resource-not-found",
    },
    "RESOURCE_002": {
        "status": 409,
        "title": "Resource Already Exists",
        "type": "https://api.engineeros.io/errors/resource-exists",
    },
    "RESOURCE_003": {
        "status": 410,
        "title": "Resource Deleted",
        "type": "https://api.engineeros.io/errors/resource-deleted",
    },
    
    # Validation errors (4xx)
    "VALIDATION_001": {
        "status": 422,
        "title": "Validation Failed",
        "type": "https://api.engineeros.io/errors/validation-failed",
    },
    "VALIDATION_002": {
        "status": 400,
        "title": "Invalid Input",
        "type": "https://api.engineeros.io/errors/invalid-input",
    },
    
    # Rate limit errors (4xx)
    "RATE_LIMIT_001": {
        "status": 429,
        "title": "Too Many Requests",
        "type": "https://api.engineeros.io/errors/rate-limit-exceeded",
    },
    
    # Server errors (5xx)
    "SERVER_001": {
        "status": 500,
        "title": "Internal Server Error",
        "type": "https://api.engineeros.io/errors/internal-error",
    },
    "SERVER_002": {
        "status": 503,
        "title": "Service Unavailable",
        "type": "https://api.engineeros.io/errors/service-unavailable",
    },
}


def create_error_response(
    error_code: str,
    detail: str | None = None,
    instance: str | None = None,
    trace_id: str | None = None,
    timestamp: str | None = None,
    **extra: Any,
) -> ErrorDetail:
    """Create standardized error response."""
    if error_code not in ERROR_CODES:
        error_code = "SERVER_001"
    
    error_info = ERROR_CODES[error_code]
    
    return ErrorDetail(
        type=error_info["type"],
        title=error_info["title"],
        status=error_info["status"],
        detail=detail,
        instance=instance,
        error_code=error_code,
        trace_id=trace_id,
        timestamp=timestamp,
        **extra,
    )
