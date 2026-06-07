"""Immutable value objects for the EngineerOS domain.

Value objects are compared by value, not identity.  They are frozen
dataclasses so they can safely be used as dict keys or set members.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillLevel:
    """Represents a skill level classification."""

    name: str          # e.g. "Backend", "Security"
    score: int         # 0-100
    tier: str          # junior, mid, senior, staff, principal

    @staticmethod
    def tier_for_score(score: int) -> str:
        """Derive tier label from numeric score."""
        if score >= 90:
            return "principal"
        if score >= 80:
            return "staff"
        if score >= 65:
            return "senior"
        if score >= 45:
            return "mid"
        return "junior"

    @classmethod
    def from_score(cls, name: str, score: int) -> SkillLevel:
        """Factory that auto-derives the tier."""
        return cls(name=name, score=score, tier=cls.tier_for_score(score))


@dataclass(frozen=True)
class ReputationScore:
    """Composite reputation across multiple dimensions."""

    debugging: int       # 0-100
    architecture: int    # 0-100
    reliability: int     # 0-100
    leadership: int      # 0-100
    system_design: int   # 0-100

    @property
    def composite(self) -> float:
        """Weighted composite score (architecture and reliability count more)."""
        weights = {
            "debugging": 1.0,
            "architecture": 1.3,
            "reliability": 1.3,
            "leadership": 0.9,
            "system_design": 1.2,
        }
        total = sum(
            getattr(self, dim) * w for dim, w in weights.items()
        )
        return round(total / sum(weights.values()), 1)


@dataclass(frozen=True)
class CareerMetrics:
    """Snapshot of career-readiness indicators."""

    interview_readiness: int     # 0-100
    promotion_readiness: int     # 0-100
    faang_probability: int       # 0-100
    growth_trajectory: str       # free-text summary

    @property
    def overall_readiness(self) -> float:
        """Average of all numeric readiness indicators."""
        return round(
            (self.interview_readiness + self.promotion_readiness + self.faang_probability) / 3, 1
        )
