from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SkillDomain(StrEnum):
    backend = "Backend"
    frontend = "Frontend"
    distributed_systems = "Distributed Systems"
    security = "Security"
    devops = "DevOps"
    ai = "AI"
    databases = "Databases"
    algorithms = "Algorithms"


class SkillScore(BaseModel):
    domain: SkillDomain
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]


class EngineerMemory(BaseModel):
    id: str
    kind: Literal["mistake", "decision", "project", "interview", "learning", "incident"]
    summary: str
    signal_strength: float = Field(ge=0, le=1)
    created_at: datetime


class Reputation(BaseModel):
    debugging: int = Field(ge=0, le=100)
    architecture: int = Field(ge=0, le=100)
    reliability: int = Field(ge=0, le=100)
    leadership: int = Field(ge=0, le=100)
    system_design: int = Field(ge=0, le=100)


class EngineerTwin(BaseModel):
    user_id: str
    title: str
    skill_scores: list[SkillScore]
    reputation: Reputation
    memory_count: int
    graph_nodes: int
    vector_embeddings: int
    updated_at: datetime


class Agent(BaseModel):
    role: str
    goal: str
    opinion: str
    memory: list[str]
    personality: str


class SimulationRequest(BaseModel):
    scenario: str = Field(examples=["Netflix outage"])
    difficulty: Literal["mid", "senior", "staff", "principal"] = "senior"
    minutes: int = Field(default=45, ge=10, le=240)


class Simulation(BaseModel):
    id: str
    scenario: str
    stakeholders: list[Agent]
    requirements: list[str]
    constraints: list[str]
    failures: list[str]
    scoring_rubric: list[str]


class Incident(BaseModel):
    id: str
    failure_mode: str
    symptoms: list[str]
    metrics: dict[str, str]
    expected_actions: list[str]
    measured_dimensions: list[str]


class RepositoryInsight(BaseModel):
    repository: str
    architecture_risks: list[str]
    dependency_hotspots: list[str]
    security_findings: list[str]
    scalability_predictions: list[str]


class CommandEvaluationRequest(BaseModel):
    user_id: str = "demo-user"
    command: str
    scenario: str
    elapsed_seconds: int = Field(default=0, ge=0)


class CommandEvaluation(BaseModel):
    diagnosis_quality: int = Field(ge=0, le=100)
    recovery_safety: int = Field(ge=0, le=100)
    communication_clarity: int = Field(ge=0, le=100)
    mentor_feedback: str
    memory_update: EngineerMemory


class CareerPrediction(BaseModel):
    user_id: str
    interview_readiness: int = Field(ge=0, le=100)
    promotion_readiness: int = Field(ge=0, le=100)
    faang_probability: int = Field(ge=0, le=100)
    growth_trajectory: str
    next_best_actions: list[str]


# ============================================================================
# SQLAlchemy ORM Models (Database layer)
# ============================================================================

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import expression


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    roles = Column(String(255), default="engineer")
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    engineer_twin = relationship("EngineerTwinORM", back_populates="user", uselist=False)
    memories = relationship("EngineerMemoryORM", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class EngineerTwinORM(Base):
    """Digital twin profile for an engineer."""

    __tablename__ = "engineer_twins"

    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    title = Column(String(255), nullable=False)
    skill_scores_json = Column(Text)
    debugging_score = Column(Integer, default=0)
    architecture_score = Column(Integer, default=0)
    reliability_score = Column(Integer, default=0)
    leadership_score = Column(Integer, default=0)
    system_design_score = Column(Integer, default=0)
    memory_count = Column(Integer, default=0)
    graph_nodes = Column(Integer, default=0)
    vector_embeddings = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="engineer_twin")
    memories = relationship("EngineerMemoryORM", back_populates="twin")

    def __repr__(self):
        return f"<EngineerTwinORM(user_id={self.user_id})>"


class EngineerMemoryORM(Base):
    """Memory record for an engineer."""

    __tablename__ = "engineer_memories"

    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    twin_id = Column(String(255), ForeignKey("engineer_twins.id"), nullable=False)
    kind = Column(String(50), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    signal_strength = Column(Integer, default=50)
    details_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="memories")
    twin = relationship("EngineerTwinORM", back_populates="memories")

    def __repr__(self):
        return f"<EngineerMemoryORM(user_id={self.user_id}, kind={self.kind})>"


class AuditLog(Base):
    """Audit log for security events and actions."""

    __tablename__ = "audit_logs"

    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(255), nullable=False, index=True)
    resource = Column(String(255), nullable=False)
    resource_id = Column(String(255), nullable=True)
    status_code = Column(Integer, nullable=False)
    details_json = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, action={self.action})>"
