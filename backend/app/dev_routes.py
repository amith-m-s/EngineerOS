"""Development and testing utilities."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from .config import get_settings
from .security import TokenData, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dev", tags=["development"])
settings = get_settings()


@router.get("/settings")
async def get_settings_info():
    """
    Get current application settings (development only).
    
    WARNING: Only available in development mode!
    Shows environment configuration for debugging.
    """
    if settings.environment == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is not available in production",
        )

    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "api_title": settings.api_title,
        "cors_origins": settings.cors_origins_list,
        "jwt_algorithm": settings.jwt_algorithm,
        "jwt_expiration_hours": settings.jwt_expiration_hours,
        "rate_limit_requests": settings.rate_limit_requests,
    }


@router.get("/me")
async def get_current_user_info(current_user: Optional[TokenData] = Depends(get_current_user)):
    """Get information about the current authenticated user."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "roles": current_user.roles,
    }
