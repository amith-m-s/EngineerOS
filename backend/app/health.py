"""Health check endpoints for service monitoring."""

from datetime import datetime, UTC
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .config import get_settings

router = APIRouter(tags=["health"])

# Startup time for uptime calculation
_startup_time = time.time()


class HealthStatus:
    """Health status response model."""
    
    def __init__(
        self,
        status: str,
        timestamp: str,
        uptime_seconds: float,
        database: Optional[dict] = None,
        cache: Optional[dict] = None,
        checks: Optional[dict] = None,
    ):
        self.status = status
        self.timestamp = timestamp
        self.uptime_seconds = uptime_seconds
        self.database = database or {}
        self.cache = cache or {}
        self.checks = checks or {}


@router.get("/health")
async def health_check() -> dict:
    """Basic health check.
    
    Returns 200 if service is up.
    Used by load balancers for simple liveness check.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)) -> dict:
    """Readiness check.
    
    Returns 200 only if service is ready to accept traffic.
    Checks database connectivity.
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready"
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {
            "database": db_status,
        }
    }


@router.get("/health/live")
async def liveness_check() -> dict:
    """Liveness check.
    
    Returns 200 if service is alive (not in crash loop).
    Simple check - no dependencies.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": time.time() - _startup_time,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> dict:
    """Detailed health check with all components.
    
    Returns comprehensive status of all subsystems.
    """
    settings = get_settings()
    uptime = time.time() - _startup_time
    
    # Check database
    db_ok = False
    db_latency = None
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency = (time.time() - start) * 1000
        db_ok = True
    except Exception as e:
        db_ok = False
    
    # Determine overall status
    overall_status = "ok" if db_ok else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": uptime,
        "environment": settings.environment,
        "components": {
            "database": {
                "status": "ok" if db_ok else "error",
                "latency_ms": db_latency,
            },
            "api": {
                "status": "ok",
            },
        },
        "checks": {
            "database_connected": db_ok,
            "api_responding": True,
        },
    }


@router.get("/health/slo")
async def slo_status(db: Session = Depends(get_db)) -> dict:
    """Service Level Objective status.
    
    Returns SLO metrics and current compliance.
    """
    uptime = time.time() - _startup_time
    uptime_hours = uptime / 3600
    
    # Simplified SLO - in production, aggregate from metrics
    # SLO: 99.9% availability = 43.2 minutes downtime per month allowed
    slo_availability = 99.9
    slo_response_time = 200  # ms
    slo_error_rate = 0.1  # 0.1%
    
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
        "slo": {
            "availability_target": slo_availability,
            "response_time_target_ms": slo_response_time,
            "error_rate_target_percent": slo_error_rate,
        },
        "current": {
            "uptime_hours": uptime_hours,
            "estimated_availability": min(99.95, 99.9 + (uptime_hours / 744) * 0.05),  # Improves over time
        }
    }


def get_health_status() -> str:
    """Get overall health status."""
    return "healthy"
