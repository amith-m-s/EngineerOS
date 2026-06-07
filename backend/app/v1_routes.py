"""API v1 routes - Version 1 of the EngineerOS API."""

from fastapi import APIRouter, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from .models import (
    EngineerTwin,
    SimulationRequest,
    Simulation,
    CareerPrediction,
)
from .pagination import PaginationParams, PaginatedResponse
from .security import get_current_user
from .services import build_demo_twin, create_simulation, predict_career

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/v1", tags=["v1"])


@router.get(
    "/twins/{user_id}",
    response_model=EngineerTwin,
    summary="Get Digital Twin",
    description="Retrieve the digital twin profile for an engineer",
)
@limiter.limit("30/minute")
async def get_v1_twin(
    request: Request,
    user_id: str,
    current_user = Depends(get_current_user),
):
    """
    Get engineer digital twin.
    
    Returns the digital twin profile including:
    - Skill scores by domain
    - Reputation metrics
    - Memory count and graph statistics
    """
    return build_demo_twin(user_id)


@router.post(
    "/simulations",
    response_model=Simulation,
    summary="Create Simulation",
    description="Create a new engineering simulation scenario",
    status_code=201,
)
@limiter.limit("20/minute")
async def create_v1_simulation(
    request: Request,
    sim_request: SimulationRequest,
    current_user = Depends(get_current_user),
):
    """
    Create a new simulation.
    
    Generates a realistic engineering scenario with:
    - Multi-stakeholder agents (SRE, Security, Product, etc)
    - Cascading failures and constraints
    - Scoring rubric for response evaluation
    """
    return create_simulation(sim_request)


@router.get(
    "/career/{user_id}",
    response_model=CareerPrediction,
    summary="Get Career Prediction",
    description="Get career prediction metrics for an engineer",
)
@limiter.limit("30/minute")
async def get_v1_career(
    request: Request,
    user_id: str,
    current_user = Depends(get_current_user),
):
    """
    Get career prediction.
    
    Returns:
    - Interview readiness (0-100)
    - Promotion readiness (0-100)
    - FAANG probability (0-100)
    - Growth trajectory analysis
    - Next best actions for career growth
    """
    return predict_career(user_id)
