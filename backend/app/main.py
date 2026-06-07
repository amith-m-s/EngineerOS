import asyncio
import logging
from contextlib import asynccontextmanager
from uuid import uuid4

import sentry_sdk
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, generate_latest
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .auth_routes import router as auth_router
from .config import get_settings
from .database import engine
from .dev_routes import router as dev_router
from .errors import ErrorDetail, create_error_response
from .logging_config import setup_logging
from .models import CommandEvaluationRequest, SimulationRequest
from .v1_routes import router as v1_router
from .health import router as health_router
from . import observability
from .middleware.correlation_id import CorrelationIdMiddleware
from .middleware.request_timing import RequestTimingMiddleware
from .events.event_bus import event_bus
from .events import handlers as event_handlers
from .services import (
    analyze_repository,
    build_demo_twin,
    create_simulation,
    evaluate_command,
    generate_incident,
    predict_career,
    recent_memories,
)

# Setup logging
logger = setup_logging()
settings = get_settings()

# Initialize Sentry if configured
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0 if settings.environment != "production" else 0.1,
        environment=settings.environment,
    )

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event handler."""
    logger.info(f"Starting EngineerOS API ({settings.environment} mode)")
    
    # Setup observability (tracing & metrics)
    logger.info("Setting up observability...")
    observability.setup_tracing()
    prometheus_reader = observability.setup_metrics()
    observability.instrument_fastapi(app)
    observability.instrument_database(engine)
    observability.instrument_http()
    logger.info("✅ Observability configured")

    # Register domain event handlers
    event_handlers.register_handlers(event_bus)
    logger.info("✅ Event handlers registered")

    # Seed demo user for development
    from .repositories.user_repository import get_user_repository
    repo = get_user_repository()
    try:
        await repo.seed_demo_user()
        logger.info("✅ Demo user seeded (demo@engineeros.io / demo1234)")
    except Exception:
        logger.debug("Demo user already exists — skipping seed")
    
    # Initialize database connection pool
    try:
        logger.info("Verifying database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        if settings.environment == "production":
            raise
    
    yield
    
    logger.info("Shutting down EngineerOS API")
    engine.dispose()  # Close all pooled connections
    logger.info("✅ Database connection pool closed")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Digital twin, engineering simulation, incident, and architecture intelligence API.",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=create_error_response(
            "RATE_LIMIT_001",
            detail="Too many requests. Please try again later.",
            trace_id=getattr(request.state, 'trace_id', str(uuid4())),
        ).dict(),
    ),
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

# Add custom middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestTimingMiddleware)

# Add trusted host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["engineeros.io", "www.engineeros.io"],
    )

# Register API routers
app.include_router(auth_router)
app.include_router(v1_router)
app.include_router(health_router)
if settings.environment != "production":
    app.include_router(dev_router)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """Add trace ID to all requests."""
    trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains" if settings.environment == "production" else "max-age=0"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "client": request.client[0] if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        },
    )
    response = await call_next(request)
    logger.info(
        f"Response: {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with RFC 7807 format."""
    trace_id = request.state.trace_id if hasattr(request.state, 'trace_id') else str(uuid4())
    
    # Build field-level errors
    field_errors = {}
    for error in exc.errors():
        field_name = ".".join(str(x) for x in error["loc"][1:]) if len(error["loc"]) > 1 else error["loc"][0]
        if field_name not in field_errors:
            field_errors[field_name] = []
        field_errors[field_name].append(error["msg"])
    
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "trace_id": trace_id,
            "errors": field_errors,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            "VALIDATION_001",
            detail="One or more validation errors occurred",
            instance=str(request.url.path),
            trace_id=trace_id,
            errors=field_errors,
        ).dict(),
    )


REQUESTS = Counter("engineeros_api_requests_total", "Total EngineerOS API requests", ["route"])


@app.get("/twin/{user_id}")
@limiter.limit("30/minute")
async def get_twin(request: Request, user_id: str):
    """Get engineer digital twin."""
    REQUESTS.labels(route="/twin/{user_id}").inc()
    return await build_demo_twin(user_id)


@app.get("/memory/{user_id}")
@limiter.limit("30/minute")
async def get_memory(request: Request, user_id: str):
    """Get engineer memories."""
    REQUESTS.labels(route="/memory/{user_id}").inc()
    return {"user_id": user_id, "memories": await recent_memories(user_id)}


@app.post("/simulations")
@limiter.limit("20/minute")
async def post_simulation(request: Request, sim_request: SimulationRequest):
    """Create a new simulation."""
    REQUESTS.labels(route="/simulations").inc()
    return create_simulation(sim_request)


@app.post("/incidents/generate")
@limiter.limit("10/minute")
async def post_incident(request: Request):
    """Generate a new incident for war room."""
    REQUESTS.labels(route="/incidents/generate").inc()
    return generate_incident()


@app.post("/incidents/evaluate-command")
@limiter.limit("20/minute")
async def post_command_evaluation(request: Request, cmd_request: CommandEvaluationRequest):
    """Evaluate a command in incident response."""
    REQUESTS.labels(route="/incidents/evaluate-command").inc()
    return await evaluate_command(cmd_request)


@app.get("/architecture/analyze")
@limiter.limit("15/minute")
async def get_architecture(request: Request, repository: str = "demo/payment-platform"):
    """Analyze repository architecture."""
    REQUESTS.labels(route="/architecture/analyze").inc()
    return analyze_repository(repository)


@app.get("/career/{user_id}")
@limiter.limit("30/minute")
async def get_career_prediction(request: Request, user_id: str):
    """Get career prediction for engineer."""
    REQUESTS.labels(route="/career/{user_id}").inc()
    return await predict_career(user_id)


@app.websocket("/ws/simulations/{simulation_id}")
async def simulation_socket(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for real-time simulation events."""
    await websocket.accept()
    logger.info(f"WebSocket connected: simulation/{simulation_id}")
    
    events = [
        {"type": "agent", "role": "SRE", "message": "Cache hit rate dropped below 41%; verify invalidation source."},
        {"type": "metric", "name": "error_budget_burn", "value": "14x"},
        {"type": "agent", "role": "Security", "message": "Emergency feature flags require audit trail retention."},
        {"type": "mentor", "message": "Score the response on evidence, reversibility, and stakeholder clarity."},
    ]
    try:
        for event in events:
            await websocket.send_json({"simulation_id": simulation_id, **event})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: simulation/{simulation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=status.WS_1011_SERVER_ERROR)


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")
