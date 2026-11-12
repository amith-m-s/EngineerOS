"""Authentication and authorization utilities."""

from datetime import UTC, datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, Field, StrictStr, ValidationError

from .config import get_settings

settings = get_settings()


class TokenData(BaseModel):
    """JWT token payload."""

    user_id: StrictStr
    email: StrictStr
    roles: list[StrictStr] = Field(default_factory=list)


class AccessToken(BaseModel):
    """Access token response."""

    access_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    user_id: str, email: str, roles: list[str], expires_delta: Optional[timedelta] = None
) -> AccessToken:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)

    to_encode = {
        "user_id": user_id,
        "email": email,
        "roles": roles,
        "exp": datetime.now(UTC) + expires_delta,
        "iat": datetime.now(UTC),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return AccessToken(access_token=encoded_jwt)


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token.

    Invalid claim types are treated as invalid credentials rather than allowing
    Pydantic validation errors to escape into the request handler.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return TokenData.model_validate(payload)
    except (JWTError, ValidationError):
        return None
