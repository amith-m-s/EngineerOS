"""Observability and telemetry configuration.

Integrates OpenTelemetry for distributed tracing, metrics, and logging.
Uses OTLP exporter (replaces deprecated Jaeger Thrift exporter).
"""

import logging

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource
from prometheus_client import Counter, Histogram, Gauge

from .config import get_settings

logger = logging.getLogger(__name__)


def setup_tracing() -> None:
    """Setup distributed tracing with OTLP exporter.
    
    Exports spans via OTLP gRPC to any compatible backend (Jaeger, Tempo, etc.).
    Gracefully degrades if the tracing backend is unavailable.
    """
    settings = get_settings()

    try:
        # Create trace provider with resource attributes
        trace_provider = TracerProvider(
            resource=Resource.create({
                "service.name": "engineeros-api",
                "service.version": settings.api_version,
                "environment": settings.environment,
            })
        )

        if settings.otlp_enabled:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.otlp_endpoint,
                insecure=settings.environment != "production",
            )
            trace_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            logger.info(f"Tracing configured: OTLP exporter → {settings.otlp_endpoint}")
        else:
            logger.info("Tracing configured: no exporter (OTLP disabled)")

        # Set global trace provider
        trace.set_tracer_provider(trace_provider)

    except Exception as exc:
        logger.warning(
            f"Tracing setup failed (app will continue without tracing): {exc}"
        )


def setup_metrics():
    """Setup Prometheus metrics collection.
    
    Exports metrics in Prometheus format on /metrics endpoint.
    """
    try:
        # Create Prometheus metric reader
        prometheus_reader = PrometheusMetricReader()

        # Create meter provider
        meter_provider = MeterProvider(
            metric_readers=[prometheus_reader],
            resource=Resource.create({
                "service.name": "engineeros-api",
                "service.version": "1.0.0",
            })
        )

        # Set global meter provider
        metrics.set_meter_provider(meter_provider)

        logger.info("Metrics configured: Prometheus exporter ready")
        return prometheus_reader

    except Exception as exc:
        logger.warning(f"Metrics setup failed (app will continue without metrics): {exc}")
        return None


def instrument_fastapi(app) -> None:
    """Instrument FastAPI application for automatic tracing.
    
    Automatically captures:
    - Request/response spans
    - Request duration
    - Request attributes (method, path, status)
    """
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="health,health/live,health/ready,metrics",
        )
        logger.info("FastAPI instrumented for tracing")
    except Exception as exc:
        logger.warning(f"FastAPI instrumentation failed: {exc}")


def instrument_database(engine) -> None:
    """Instrument SQLAlchemy for database tracing.
    
    Automatically captures:
    - SQL query spans
    - Query duration
    - Connection pool stats
    """
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument(
            engine=engine,
            service_name="engineeros-api",
        )
        logger.info("SQLAlchemy instrumented for tracing")
    except Exception as exc:
        logger.warning(f"SQLAlchemy instrumentation failed: {exc}")


def instrument_http() -> None:
    """Instrument HTTP requests for tracing.
    
    Automatically captures outgoing HTTP calls.
    """
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        RequestsInstrumentor().instrument()
        logger.info("HTTP requests instrumented for tracing")
    except Exception as exc:
        logger.warning(f"HTTP instrumentation failed: {exc}")


# Custom Prometheus metrics
class CustomMetrics:
    """Custom Prometheus metrics for EngineerOS."""
    
    def __init__(self):
        # Request metrics
        self.request_duration = Histogram(
            "engineeros_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint", "status"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
        )
        
        self.request_count = Counter(
            "engineeros_requests_total",
            "Total requests",
            ["method", "endpoint", "status"]
        )
        
        # Authentication metrics
        self.login_attempts = Counter(
            "engineeros_login_attempts_total",
            "Login attempts",
            ["result"]  # success, failure
        )
        
        self.active_tokens = Gauge(
            "engineeros_active_tokens",
            "Active JWT tokens"
        )
        
        # Database metrics
        self.db_query_duration = Histogram(
            "engineeros_db_query_duration_seconds",
            "Database query duration",
            ["query_type"],  # select, insert, update, delete
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
        )
        
        self.db_connection_pool_size = Gauge(
            "engineeros_db_pool_size",
            "Database connection pool size",
            ["pool_type"]  # checked_out, available
        )
        
        # Error metrics
        self.errors_total = Counter(
            "engineeros_errors_total",
            "Total errors",
            ["error_code", "endpoint"]
        )
        
        self.error_rate = Gauge(
            "engineeros_error_rate",
            "Error rate (errors per minute)"
        )
        
        # Business metrics
        self.simulations_created = Counter(
            "engineeros_simulations_created_total",
            "Total simulations created",
            ["difficulty"]
        )
        
        self.memories_recorded = Counter(
            "engineeros_memories_recorded_total",
            "Total memories recorded",
            ["kind"]  # mistake, decision, project, etc
        )
        
        self.career_predictions = Counter(
            "engineeros_career_predictions_total",
            "Total career predictions generated",
            ["prediction_type"]  # readiness, trajectory, etc
        )
        
        # System metrics
        self.uptime_seconds = Gauge(
            "engineeros_uptime_seconds",
            "Application uptime in seconds"
        )
        
        self.last_error = Gauge(
            "engineeros_last_error_timestamp",
            "Unix timestamp of last error"
        )


# Global metrics instance
metrics_instance = CustomMetrics()


def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record request metrics."""
    metrics_instance.request_duration.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).observe(duration)
    
    metrics_instance.request_count.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()


def record_login(result: str):
    """Record login attempt."""
    metrics_instance.login_attempts.labels(result=result).inc()


def record_db_query(query_type: str, duration: float):
    """Record database query."""
    metrics_instance.db_query_duration.labels(query_type=query_type).observe(duration)


def record_error(error_code: str, endpoint: str = "unknown"):
    """Record error occurrence."""
    metrics_instance.errors_total.labels(
        error_code=error_code,
        endpoint=endpoint
    ).inc()


def record_simulation(difficulty: str):
    """Record simulation creation."""
    metrics_instance.simulations_created.labels(difficulty=difficulty).inc()


def record_memory(kind: str):
    """Record memory record."""
    metrics_instance.memories_recorded.labels(kind=kind).inc()


def record_career_prediction(prediction_type: str):
    """Record career prediction."""
    metrics_instance.career_predictions.labels(prediction_type=prediction_type).inc()
