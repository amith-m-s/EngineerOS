"""SLO (Service Level Objective) and SLI (Service Level Indicator) definitions."""

from dataclasses import dataclass
from typing import List


@dataclass
class SLI:
    """Service Level Indicator - measurable metric."""
    
    name: str
    description: str
    metric_name: str
    threshold: float
    unit: str


@dataclass
class SLO:
    """Service Level Objective - target for SLIs."""
    
    name: str
    description: str
    target: float  # e.g., 99.9 for 99.9% availability
    period_days: int
    slis: List[SLI]


# Availability SLI & SLO
availability_sli = SLI(
    name="Availability",
    description="Percentage of time service is up and responding",
    metric_name="engineeros_availability_percent",
    threshold=99.9,
    unit="percent"
)

availability_slo = SLO(
    name="API Availability",
    description="Service must be available 99.9% of the time",
    target=99.9,  # 43.2 minutes downtime per month
    period_days=30,
    slis=[availability_sli]
)

# Response Time SLI & SLO
response_time_sli = SLI(
    name="Response Time (p95)",
    description="95th percentile request latency",
    metric_name="engineeros_request_duration_seconds",
    threshold=0.2,  # 200ms
    unit="seconds"
)

latency_slo = SLO(
    name="Response Latency",
    description="API response time p95 <= 200ms",
    target=200,  # milliseconds
    period_days=30,
    slis=[response_time_sli]
)

# Error Rate SLI & SLO
error_rate_sli = SLI(
    name="Error Rate",
    description="Percentage of requests resulting in errors (5xx)",
    metric_name="engineeros_error_rate_percent",
    threshold=0.1,  # 0.1%
    unit="percent"
)

error_rate_slo = SLO(
    name="Error Rate",
    description="Error rate (5xx responses) <= 0.1%",
    target=0.1,
    period_days=30,
    slis=[error_rate_sli]
)

# Authentication Success Rate SLI & SLO
auth_success_sli = SLI(
    name="Auth Success Rate",
    description="Percentage of login attempts that succeed",
    metric_name="engineeros_auth_success_rate",
    threshold=99.0,  # 99% of valid attempts should succeed
    unit="percent"
)

auth_slo = SLO(
    name="Authentication",
    description="Valid login attempts succeed 99% of the time",
    target=99.0,
    period_days=30,
    slis=[auth_success_sli]
)

# Database Response Time SLI & SLO
db_response_sli = SLI(
    name="Database Query Time (p95)",
    description="95th percentile database query latency",
    metric_name="engineeros_db_query_duration_seconds",
    threshold=0.1,  # 100ms
    unit="seconds"
)

db_slo = SLO(
    name="Database Performance",
    description="Database queries p95 <= 100ms",
    target=100,  # milliseconds
    period_days=30,
    slis=[db_response_sli]
)

# All SLOs
ALL_SLOS = [
    availability_slo,
    latency_slo,
    error_rate_slo,
    auth_slo,
    db_slo,
]

# SLO Summary for documentation
SLO_SUMMARY = {
    "availability": {
        "target": 99.9,
        "downtime_allowed_monthly": "43.2 minutes",
        "downtime_allowed_yearly": "8.77 hours",
    },
    "latency_p95": {
        "target": "200ms",
        "description": "95% of requests respond within 200ms",
    },
    "error_rate": {
        "target": "0.1%",
        "description": "Less than 0.1% of requests result in 5xx errors",
    },
    "authentication": {
        "target": "99% success rate",
        "description": "Valid login attempts succeed 99% of the time",
    },
    "database_performance": {
        "target": "100ms p95",
        "description": "95% of database queries complete within 100ms",
    },
}
