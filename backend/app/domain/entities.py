"""Pure domain entities — no SQLAlchemy, no Pydantic dependency for core logic.

These represent the core business concepts of EngineerOS.  They are deliberately
plain Python dataclasses so the domain layer stays framework-agnostic and can be
tested, serialised, or mapped to any persistence backend without coupling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Literal
from uuid import uuid4


# ---------------------------------------------------------------------------
# Engineer Profile
# ---------------------------------------------------------------------------

@dataclass
class EngineerProfile:
    """Core representation of an engineer in the system."""

    id: str = field(default_factory=lambda: f"eng_{uuid4().hex[:12]}")
    user_id: str = ""
    email: str = ""
    full_name: str = ""
    title: str = ""
    roles: list[str] = field(default_factory=lambda: ["engineer"])
    is_active: bool = True
    is_verified: bool = False
    password_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Skill Assessment
# ---------------------------------------------------------------------------

SkillDomainLiteral = Literal[
    "Backend", "Frontend", "Distributed Systems", "Security",
    "DevOps", "AI", "Databases", "Algorithms",
]


@dataclass
class SkillAssessment:
    """A single skill assessment for an engineer."""

    domain: SkillDomainLiteral
    score: int  # 0-100
    confidence: float  # 0.0-1.0
    evidence: list[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Incident Record
# ---------------------------------------------------------------------------

@dataclass
class IncidentRecord:
    """Record of an engineering incident (war-room scenario)."""

    id: str = field(default_factory=lambda: f"inc_{uuid4().hex[:10]}")
    failure_mode: str = ""
    symptoms: list[str] = field(default_factory=list)
    metrics: dict[str, str] = field(default_factory=dict)
    expected_actions: list[str] = field(default_factory=list)
    measured_dimensions: list[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Simulation Session
# ---------------------------------------------------------------------------

@dataclass
class SimulationSession:
    """An active simulation session."""

    id: str = field(default_factory=lambda: f"sim_{uuid4().hex[:10]}")
    scenario: str = ""
    difficulty: Literal["mid", "senior", "staff", "principal"] = "senior"
    minutes: int = 45
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    score: float | None = None


# ---------------------------------------------------------------------------
# Memory Entry
# ---------------------------------------------------------------------------

MemoryKind = Literal["mistake", "decision", "project", "interview", "learning", "incident"]


@dataclass
class MemoryEntry:
    """A single memory stored for an engineer's digital twin."""

    id: str = field(default_factory=lambda: f"mem_{uuid4().hex[:10]}")
    user_id: str = ""
    kind: MemoryKind = "learning"
    summary: str = ""
    signal_strength: float = 0.5  # 0.0-1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
