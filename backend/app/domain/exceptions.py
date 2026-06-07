"""Domain exceptions with error codes.

These are raised by domain/service logic and caught by the API layer
to produce appropriate HTTP responses.
"""

from __future__ import annotations


class DomainException(Exception):
    """Base exception for all domain-level errors."""

    error_code: str = "DOMAIN_000"
    status_code: int = 500

    def __init__(self, message: str = "A domain error occurred", *, error_code: str | None = None):
        self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)


class EntityNotFound(DomainException):
    """Raised when a requested entity does not exist."""

    error_code = "RESOURCE_001"
    status_code = 404

    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(f"{entity_type} with id '{entity_id}' not found")
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntity(DomainException):
    """Raised when attempting to create an entity that already exists."""

    error_code = "RESOURCE_002"
    status_code = 409

    def __init__(self, entity_type: str, key: str, value: str):
        super().__init__(f"{entity_type} with {key}='{value}' already exists")
        self.entity_type = entity_type
        self.key = key
        self.value = value


class InvalidOperation(DomainException):
    """Raised when an operation violates a business rule."""

    error_code = "VALIDATION_002"
    status_code = 400

    def __init__(self, message: str = "Invalid operation"):
        super().__init__(message)


class AuthenticationFailed(DomainException):
    """Raised when authentication credentials are invalid."""

    error_code = "AUTH_001"
    status_code = 401

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class InsufficientPermissions(DomainException):
    """Raised when a user lacks required permissions."""

    error_code = "AUTH_004"
    status_code = 403

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


class TokenExpired(DomainException):
    """Raised when a JWT token has expired."""

    error_code = "AUTH_002"
    status_code = 401

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class TokenInvalid(DomainException):
    """Raised when a JWT token is malformed or tampered with."""

    error_code = "AUTH_003"
    status_code = 401

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)
