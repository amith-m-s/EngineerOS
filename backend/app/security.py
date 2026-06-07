"""Security utilities and middleware."""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import TokenData, decode_access_token
from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> TokenData:
    """Dependency to get current authenticated user from JWT token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = decode_access_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenData]:
    """Dependency to get optional authenticated user from JWT token."""
    if credentials is None:
        return None

    token = credentials.credentials
    token_data = decode_access_token(token)
    return token_data


def require_role(*required_roles: str):
    """Dependency factory to require specific roles."""

    async def check_role(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        user_roles_set = set(current_user.roles)
        required_roles_set = set(required_roles)

        if not user_roles_set.intersection(required_roles_set):
            logger.warning(
                f"User {current_user.user_id} attempted access with insufficient roles. "
                f"Required: {required_roles}, Has: {current_user.roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return check_role
