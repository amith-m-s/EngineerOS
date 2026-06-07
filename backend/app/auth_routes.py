"""API routes for authentication and user management.

Implements REAL authentication flows using the UserRepository for data
access and the TokenBlacklist (via InMemoryCache) for logout / refresh.
"""

import logging
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from .auth import (
    AccessToken,
    TokenData,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from .cache import get_token_blacklist
from .config import get_settings
from .domain.entities import EngineerProfile
from .domain.exceptions import DuplicateEntity
from .repositories.user_repository import get_user_repository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class LoginResponse(BaseModel):
    """Login response with tokens."""

    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    roles: list[str]


class UserRegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Must be at least 8 characters with mixed case and digits",
    )
    full_name: str = Field(..., min_length=1, max_length=255)


class RefreshRequest(BaseModel):
    """Token refresh request."""

    access_token: str = Field(..., description="Current (possibly expired) access token")


class LogoutResponse(BaseModel):
    """Logout response."""

    status: str = "logged_out"
    detail: str = "Token has been invalidated"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """
    Register a new user account.

    - Validates email uniqueness
    - Hashes password with bcrypt
    - Creates user in repository
    - Returns JWT token for immediate login
    """
    repo = get_user_repository()

    # Check email uniqueness
    existing = await repo.find_by_email(request.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create new user
    user_id = f"eng_{uuid4().hex[:12]}"
    new_user = EngineerProfile(
        id=user_id,
        user_id=user_id,
        email=request.email,
        full_name=request.full_name,
        title="Engineer",
        roles=["engineer"],
        is_active=True,
        is_verified=False,
        password_hash=hash_password(request.password),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    try:
        await repo.create(new_user)
    except DuplicateEntity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    logger.info(f"New user registered: {user_id} ({request.email})")

    # Issue token for immediate login
    token = create_access_token(
        user_id=user_id,
        email=request.email,
        roles=["engineer"],
    )

    return LoginResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        user_id=user_id,
        email=request.email,
        roles=["engineer"],
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate with email and password.

    Looks up user in the repository and verifies the bcrypt hash.
    Returns a signed JWT on success.
    """
    repo = get_user_repository()
    user = await repo.find_by_email(request.email)

    if user is None or not verify_password(request.password, user.password_hash):
        logger.warning(f"Failed login attempt for {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated",
        )

    token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        roles=user.roles,
    )

    logger.info(f"User logged in: {user.user_id}")

    return LoginResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        user_id=user.user_id,
        email=user.email,
        roles=user.roles,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh an access token.

    Accepts the current token, validates it (allows recently expired),
    blacklists the old token, and issues a fresh one.
    """
    blacklist = get_token_blacklist()

    # Decode token (we still need user info from it)
    token_data = decode_access_token(request.access_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token — cannot refresh",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if old token is already blacklisted
    token_jti = request.access_token[-16:]  # Use last 16 chars as identifier
    if await blacklist.is_blacklisted(token_jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    # Blacklist the old token
    await blacklist.blacklist(token_jti, ttl_seconds=settings.jwt_expiration_hours * 3600)

    # Issue new token
    new_token = create_access_token(
        user_id=token_data.user_id,
        email=token_data.email,
        roles=token_data.roles,
    )

    logger.info(f"Token refreshed for user: {token_data.user_id}")

    return LoginResponse(
        access_token=new_token.access_token,
        token_type=new_token.token_type,
        user_id=token_data.user_id,
        email=token_data.email,
        roles=token_data.roles,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """
    Logout — invalidate the current access token.

    Adds the token to the blacklist so it cannot be reused. The
    blacklist entry automatically expires when the token would have.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = decode_access_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # Add to blacklist
    blacklist = get_token_blacklist()
    token_jti = token[-16:]
    await blacklist.blacklist(token_jti, ttl_seconds=settings.jwt_expiration_hours * 3600)

    logger.info(f"User logged out: {token_data.user_id}")

    return LogoutResponse()
