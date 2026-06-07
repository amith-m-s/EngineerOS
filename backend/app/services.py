import json
from datetime import UTC, datetime
from uuid import uuid4

from .models import (
    Agent,
    CareerPrediction,
    CommandEvaluation,
    CommandEvaluationRequest,
    EngineerMemory,
    EngineerTwin,
    Incident,
    Reputation,
    RepositoryInsight,
    Simulation,
    SimulationRequest,
    SkillDomain,
    SkillScore,
)

from .repositories.twin_repository import get_twin_repository, TwinRecord
from .repositories.memory_repository import get_memory_repository
from .domain.entities import MemoryEntry


async def build_demo_twin(user_id: str) -> EngineerTwin:
    """Retrieve or create the user's digital twin snapshot."""
    twin_repo = get_twin_repository()
    record = await twin_repo.find_by_user_id(user_id)
    
    if not record:
        evidence = {
            SkillDomain.backend: ["payment-service commits", "API design reviews", "incident remediations"],
            SkillDomain.frontend: ["dashboard components", "accessibility fixes"],
            SkillDomain.distributed_systems: ["Kafka partition strategy", "cache stampede diagnosis"],
            SkillDomain.security: ["auth threat modeling gaps", "secret rotation exercise"],
            SkillDomain.devops: ["Kubernetes rollout plans", "OpenTelemetry adoption"],
            SkillDomain.ai: ["RAG prototype", "agent evaluation traces"],
            SkillDomain.databases: ["Postgres indexing work", "Neo4j schema design"],
            SkillDomain.algorithms: ["search ranking interview drills", "latency-aware routing"]
        }
        scores = [91, 73, 84, 68, 88, 76, 81, 79]
        skill_scores = [
            SkillScore(domain=domain, score=scores[index], confidence=0.74 + index * 0.02, evidence=evidence[domain])
            for index, domain in enumerate(SkillDomain)
        ]
        
        skill_scores_json = json.dumps([s.model_dump() for s in skill_scores])
        
        record = TwinRecord(
            user_id=user_id,
            title="Senior Backend Engineer trending toward Staff",
            skill_scores_json=skill_scores_json,
            debugging_score=89,
            architecture_score=86,
            reliability_score=92,
            leadership_score=74,
            system_design_score=88,
            memory_count=3,
            graph_nodes=3184,
            vector_embeddings=12033
        )
        await twin_repo.create(record)
    else:
        try:
            skills_data = json.loads(record.skill_scores_json)
            skill_scores = [SkillScore(**s) for s in skills_data]
        except Exception:
            skill_scores = []

    return EngineerTwin(
        user_id=record.user_id,
        title=record.title,
        skill_scores=skill_scores,
        reputation=Reputation(
            debugging=record.debugging_score,
            architecture=record.architecture_score,
            reliability=record.reliability_score,
            leadership=record.leadership_score,
            system_design=record.system_design_score
        ),
        memory_count=record.memory_count,
        graph_nodes=record.graph_nodes,
        vector_embeddings=record.vector_embeddings,
        updated_at=record.updated_at,
    )


async def recent_memories(user_id: str) -> list[EngineerMemory]:
    """Retrieve user memories from MemoryRepository, seeding defaults if empty."""
    memory_repo = get_memory_repository()
    memories = await memory_repo.find_by_user_id(user_id)
    
    if not memories:
        now = datetime.now(UTC)
        defaults = [
            MemoryEntry(
                id="mem_decision_retry_strategy",
                user_id=user_id,
                kind="decision",
                summary="Prefers event-driven retries with bounded dead-letter handling for financial workflows.",
                signal_strength=0.91,
                created_at=now
            ),
            MemoryEntry(
                id="mem_mistake_auth_modeling",
                user_id=user_id,
                kind="mistake",
                summary="Underweights authentication abuse cases when incident timers are active.",
                signal_strength=0.78,
                created_at=now
            ),
            MemoryEntry(
                id="mem_learning_kafka_lag",
                user_id=user_id,
                kind="learning",
                summary="Improved diagnosis speed for consumer lag by correlating partition skew with deploy windows.",
                signal_strength=0.86,
                created_at=now
            )
        ]
        for item in defaults:
            await memory_repo.create(item)
        memories = defaults
        
    return [
        EngineerMemory(
            id=m.id,
            kind=m.kind,
            summary=m.summary,
            signal_strength=m.signal_strength,
            created_at=m.created_at
        )
        for m in memories
    ]


def create_simulation(request: SimulationRequest) -> Simulation:
    """Create a simulation config."""
    agents = [
        Agent(
            role="CTO",
            goal="Protect strategic reliability goals without freezing product delivery.",
            opinion="The fix must reduce future blast radius, not just restore the current deploy.",
            memory=["User previously chose a reversible migration during a billing outage."],
            personality="Direct, systems-oriented, occasionally impatient.",
        ),
        Agent(
            role="Product Manager",
            goal="Keep the launch credible for enterprise customers.",
            opinion="A partial rollback is acceptable if user-facing messaging is clear.",
            memory=["User tends to explain technical tradeoffs well to non-engineers."],
            personality="Pragmatic and deadline-sensitive.",
        ),
        Agent(
            role="SRE",
            goal="Reduce mean time to recovery and preserve evidence.",
            opinion="Do not restart everything until the saturation source is isolated.",
            memory=["User is strong at metrics correlation but sometimes skips runbook updates."],
            personality="Calm, skeptical, precise.",
        ),
        Agent(
            role="Security Engineer",
            goal="Prevent reliability shortcuts from creating an exploit path.",
            opinion="Emergency feature flags still need audit trails.",
            memory=["User missed rate-limit implications in an auth redesign."],
            personality="Persistent and adversarial in useful ways.",
        ),
    ]

    return Simulation(
        id=f"sim_{uuid4().hex[:10]}",
        scenario=request.scenario,
        stakeholders=agents,
        requirements=[
            "Restore core user journey before the incident deadline.",
            "Explain tradeoffs to stakeholders with measurable risk.",
            "Produce a follow-up architecture improvement plan.",
        ],
        constraints=[
            f"{request.minutes} minute response window.",
            "No direct database writes without approval from SRE and Security.",
            "Telemetry is incomplete for one downstream service.",
        ],
        failures=[
            "Regional traffic spike causes queue saturation.",
            "Cache invalidation bug amplifies database read load.",
            "A rollback path conflicts with a schema migration.",
        ],
        scoring_rubric=[
            "Diagnosis speed",
            "Recovery quality",
            "Architecture judgment",
            "Communication clarity",
            "Operational safety",
        ],
    )


def generate_incident() -> Incident:
    """Generate mock incident properties."""
    return Incident(
        id=f"inc_{uuid4().hex[:10]}",
        failure_mode="Distributed cache stampede",
        symptoms=[
            "API p99 latency increased from 180ms to 2.4s.",
            "PostgreSQL read replicas are near connection exhaustion.",
            "Redis hit rate dropped below 41%.",
        ],
        metrics={"mttr_target": "15m", "error_budget_burn": "14x", "affected_regions": "3"},
        expected_actions=[
            "Confirm cache key invalidation pattern.",
            "Throttle non-critical reads.",
            "Enable request coalescing or stale-while-revalidate.",
            "Capture post-incident architecture decision record.",
        ],
        measured_dimensions=["Diagnosis speed", "Recovery quality", "Reliability score", "Communication"],
    )


def analyze_repository(repository: str) -> RepositoryInsight:
    """Examine code layout hotspots."""
    return RepositoryInsight(
        repository=repository,
        architecture_risks=[
            "Synchronous dependency chain from checkout to recommendation service increases blast radius.",
            "Background workers lack idempotency evidence in git history.",
        ],
        dependency_hotspots=[
            "payments/ledger.py imported by 18 modules.",
            "shared/auth middleware controls three critical request paths.",
        ],
        security_findings=[
            "Secrets scanning should be enforced before merge.",
            "Admin APIs need explicit authorization boundary tests.",
        ],
        scalability_predictions=[
            "Search indexing pipeline will saturate at roughly 4.2x current traffic without partitioning.",
            "Redis memory pressure likely before PostgreSQL CPU saturation.",
        ],
    )


async def evaluate_command(request: CommandEvaluationRequest) -> CommandEvaluation:
    """Evaluate an SRE terminal command and update user digital twin stats in repository."""
    command = request.command.lower()
    diagnosis_bonus = sum(token in command for token in ["p99", "cache", "lag", "deploy", "metric", "trace"]) * 8
    safety_bonus = sum(token in command for token in ["rollback", "blast", "stale", "throttle", "coalescing"]) * 7
    communication_bonus = sum(token in command for token in ["stakeholder", "brief", "customer", "risk", "tradeoff"]) * 9

    diagnosis = min(96, 54 + diagnosis_bonus)
    safety = min(94, 50 + safety_bonus)
    communication = min(92, 48 + communication_bonus)

    if diagnosis > 75 and safety > 70:
        feedback = "Strong incident command: evidence-first diagnosis with a safer recovery path."
    elif diagnosis > safety:
        feedback = "Good diagnosis signal, but the recovery plan needs more blast-radius control."
    else:
        feedback = "Recovery instinct is useful; strengthen it with clearer telemetry evidence."

    memory_id = f"mem_cmd_{uuid4().hex[:10]}"
    now = datetime.now(UTC)
    signal = round((diagnosis + safety + communication) / 300, 2)
    summary = f"Evaluated command in {request.scenario}: {request.command}"

    memory_entry = MemoryEntry(
        id=memory_id,
        user_id=request.user_id,
        kind="incident",
        summary=summary,
        signal_strength=signal,
        created_at=now
    )

    memory_repo = get_memory_repository()
    await memory_repo.create(memory_entry)

    twin_repo = get_twin_repository()
    twin_rec = await twin_repo.find_by_user_id(request.user_id)

    if not twin_rec:
        await build_demo_twin(request.user_id)
        twin_rec = await twin_repo.find_by_user_id(request.user_id)

    if twin_rec:
        updates = {
            "debugging_score": min(100, twin_rec.debugging_score + round(diagnosis / 15)),
            "reliability_score": min(100, twin_rec.reliability_score + round(safety / 15)),
            "system_design_score": min(100, twin_rec.system_design_score + round(communication / 20)),
            "memory_count": await memory_repo.count_for_user(request.user_id)
        }
        await twin_repo.upsert_for_user(request.user_id, updates)

    return CommandEvaluation(
        diagnosis_quality=diagnosis,
        recovery_safety=safety,
        communication_clarity=communication,
        mentor_feedback=feedback,
        memory_update=EngineerMemory(
            id=memory_id,
            kind="incident",
            summary=summary,
            signal_strength=signal,
            created_at=now
        )
    )


async def predict_career(user_id: str) -> CareerPrediction:
    """Predict career metrics dynamically based on digital twin scores in repository."""
    twin_repo = get_twin_repository()
    twin_rec = await twin_repo.find_by_user_id(user_id)
    if not twin_rec:
        await build_demo_twin(user_id)
        twin_rec = await twin_repo.find_by_user_id(user_id)

    architecture = twin_rec.architecture_score if twin_rec else 86
    system_design = twin_rec.system_design_score if twin_rec else 88
    reliability = twin_rec.reliability_score if twin_rec else 92

    interview_readiness = min(100, system_design + 3)
    promotion_readiness = min(100, round((architecture + reliability) / 2))
    faang_probability = min(100, round((reliability * 0.4) + (system_design * 0.5) + 10))

    if promotion_readiness > 88:
        growth_trajectory = "Accelerating to Principal Engineer based on elite system design and architectural leadership."
    elif promotion_readiness > 80:
        growth_trajectory = "Accelerating toward Staff Engineer. High design capability with growing execution reliability."
    else:
        growth_trajectory = "Strong Senior track. Focus on distributed systems reliability and incident brief clarity."

    return CareerPrediction(
        user_id=user_id,
        interview_readiness=interview_readiness,
        promotion_readiness=promotion_readiness,
        faang_probability=faang_probability,
        growth_trajectory=growth_trajectory,
        next_best_actions=[
            "Run two security-heavy system design simulations.",
            "Capture architecture decision records for incident recovery choices.",
            "Practice executive-level incident briefs under a 5 minute limit."
        ]
    )
