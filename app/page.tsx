"use client";

import {
  Activity,
  Blocks,
  BrainCircuit,
  Code2,
  Command,
  Gauge,
  GitBranch,
  Network,
  Play,
  Radar,
  RefreshCcw,
  ServerCrash,
  ShieldAlert,
  Sparkles,
  Users,
  Workflow,
  Lock,
  Loader2
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";

import ArchitectureMap from "./components/ArchitectureMap";
import IncidentBoard from "./components/IncidentBoard";
import MemoryStream from "./components/MemoryStream";
import ReputationStrip from "./components/ReputationStrip";
import Sidebar from "./components/Sidebar";
import SimulationPanel from "./components/SimulationPanel";
import SkillGrid from "./components/SkillGrid";
import TwinGraph from "./components/TwinGraph";
import { useAuth, useFetch, useMutation, useWebSocket, useAnimatedValue } from "./hooks";
import api from "./lib/api";

/* ── Data ──────────────────────────────────────────────────────── */

const skills = [
  { name: "Backend", score: 91, color: "#0d9488", icon: Code2 },
  { name: "Distributed Systems", score: 84, color: "#3867d6", icon: Network },
  { name: "Security", score: 68, color: "#f9735b", icon: ShieldAlert },
  { name: "AI Systems", score: 76, color: "#7c4dff", icon: BrainCircuit },
  { name: "DevOps", score: 88, color: "#d99a28", icon: Activity },
  { name: "Databases", score: 81, color: "#0f766e", icon: Blocks },
  { name: "Frontend", score: 73, color: "#ef5da8", icon: Sparkles },
  { name: "Algorithms", score: 79, color: "#4f46e5", icon: Radar }
];

const agents = [
  { role: "CTO", stance: "Pushes long-term platform bets", color: "#0d9488" },
  { role: "Senior Engineer", stance: "Challenges implementation tradeoffs", color: "#3867d6" },
  { role: "Product Manager", stance: "Defends deadline and customer impact", color: "#d99a28" },
  { role: "SRE", stance: "Tracks blast radius and recovery time", color: "#f9735b" },
  { role: "Security", stance: "Reviews abuse paths and secrets exposure", color: "#7c4dff" }
];

const incidents = [
  { name: "Kafka consumer lag", detail: "Checkout events are 18 minutes behind.", time: "07:42", severity: "#f9735b" },
  { name: "Redis cache stampede", detail: "Profile API p99 climbed from 180ms to 2.4s.", time: "12:09", severity: "#d99a28" },
  { name: "Suspicious auth traffic", detail: "Credential stuffing pattern across 23 regions.", time: "03:31", severity: "#ef4444" }
];

const events = [
  "Captured a design preference for event-driven retries over cron repair jobs.",
  "Marked weak signal: authentication threat modeling under time pressure.",
  "Updated promotion readiness after resolving a distributed cache failure.",
  "Linked git history from payment-service to reliability score movement."
];

const simulations = [
  {
    title: "Netflix-style regional outage",
    detail: "Traffic shifted to a degraded region while recommendation and billing services disagree on user state.",
    pressure: "P0",
    clock: "45m"
  },
  {
    title: "Google-scale search backend",
    detail: "Index freshness drops while ranking latency spikes across personalized search shards.",
    pressure: "P1",
    clock: "90m"
  },
  {
    title: "Uber dispatch platform",
    detail: "Driver matching degrades during surge traffic while geospatial writes are delayed.",
    pressure: "P0",
    clock: "30m"
  }
];

const repoFindings = [
  "payments/ledger.ts is a blast-radius hotspot across 18 call paths",
  "Auth middleware lacks explicit boundary tests for admin routes",
  "Search indexing pipeline saturates at 4.2x current traffic",
  "Queue retry policy risks duplicate side effects during failover"
];

const reputation = [
  { label: "Debugging", score: 89, delta: "+7", icon: ServerCrash, color: "#f9735b" },
  { label: "Architecture", score: 86, delta: "+5", icon: Workflow, color: "#3867d6" },
  { label: "Reliability", score: 92, delta: "+9", icon: Gauge, color: "#0d9488" },
  { label: "Leadership", score: 74, delta: "+3", icon: Users, color: "#d99a28" },
  { label: "System Design", score: 88, delta: "+6", icon: Network, color: "#7c4dff" }
];

const runbookActions = [
  {
    id: "contain",
    label: "Contain blast radius",
    detail: "Shift non-critical reads to stale cache and freeze risky deploy lanes.",
    gain: 18
  },
  {
    id: "diagnose",
    label: "Correlate telemetry",
    detail: "Compare cache hit rate, DB pool pressure, and deploy window events.",
    gain: 22
  },
  {
    id: "recover",
    label: "Recover safely",
    detail: "Enable request coalescing before rolling regional traffic back.",
    gain: 28
  },
  {
    id: "learn",
    label: "Write memory update",
    detail: "Store the decision trace as Engineer DNA evidence.",
    gain: 16
  }
];

const initialTranscript = [
  {
    speaker: "SRE",
    message: "I need proof before restart-all. Show cache hit rate, read replica pressure, and deploy timing."
  },
  {
    speaker: "Security",
    message: "Emergency flags are fine, but audit trails stay on. No silent admin bypass."
  },
  {
    speaker: "CTO",
    message: "I care about the permanent design move. What changes after the incident?"
  }
];

const careerSignals = [
  { label: "Staff readiness", value: "82%", detail: "Strong architecture signal, needs broader leadership evidence." },
  { label: "Interview readiness", value: "91%", detail: "System design pacing and tradeoff clarity are above bar." },
  { label: "FAANG probability", value: "76%", detail: "Improves with security depth and distributed systems storytelling." }
];

type StagePointer = {
  x: number;
  y: number;
  active: boolean;
};

/* ── Page ──────────────────────────────────────────────────────── */

function AuthConsole() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const { login, register, error, clearError, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isRegister) {
      await register(email, password, fullName);
    } else {
      await login(email, password);
    }
  };

  const handleDemoMode = async () => {
    await login("demo@engineeros.io", "demo1234");
  };

  return (
    <div className="authContainer">
      <div className="gridBackground" />
      <div className="authConsole">
        <div className="authHeader">
          <div className="logoRing">
            <BrainCircuit className="pulseGlow" size={32} />
          </div>
          <h1>EngineerOS</h1>
          <p>Decrypting neural skill trees and live telemetry systems</p>
        </div>

        {error && (
          <div className="authErrorAlert">
            <Lock size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div className="authFormGroup">
              <label htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                type="text"
                className="authInput"
                placeholder="Devin AI"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          )}

          <div className="authFormGroup">
            <label htmlFor="email">Security Token (Email)</label>
            <input
              id="email"
              type="email"
              className="authInput"
              placeholder="token@engineeros.io"
              required
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (error) clearError();
              }}
            />
          </div>

          <div className="authFormGroup">
            <label htmlFor="password">Access Key (Password)</label>
            <input
              id="password"
              type="password"
              className="authInput"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) clearError();
              }}
            />
          </div>

          <button type="submit" className="authSubmitBtn" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="spin" size={18} />
                <span>Decrypting...</span>
              </>
            ) : (
              <span>{isRegister ? "Register Credentials" : "Authorize Session"}</span>
            )}
          </button>
        </form>

        <button type="button" className="demoModeBtn" onClick={handleDemoMode} disabled={isLoading}>
          Initialize Sandbox Demo
        </button>

        <div className="authToggleMode">
          {isRegister ? "Already pre-registered?" : "Need initial workspace?"}
          <button
            type="button"
            className="authToggleLink"
            onClick={() => {
              setIsRegister(!isRegister);
              clearError();
            }}
          >
            {isRegister ? "Authorize Sign In" : "Register DNA"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const { user, isAuthenticated, logout, isLoading: authLoading } = useAuth();

  const [activeSection, setActiveSection] = useState("twin");
  const [simulationIndex, setSimulationIndex] = useState(0);
  const [simulationId, setSimulationId] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [toast, setToast] = useState("Engineer DNA synced from 8,421 memory nodes.");
  const [showGraph, setShowGraph] = useState(false);
  const [commandText, setCommandText] = useState("check p99, cache hit rate, deploy diff");
  const [transcript, setTranscript] = useState(initialTranscript);
  const [completedActions, setCompletedActions] = useState<string[]>([]);
  const [recoveryScore, setRecoveryScore] = useState(31);
  const pointerRef = useRef<StagePointer>({ x: 0, y: 0, active: false });

  // Fetch twin snapshot dynamically from backend API
  const { data: twinData, refetch: refetchTwin, isLoading: twinLoading } = useFetch(
    user ? `twin_${user.userId}` : "",
    () => api.twin.get(user?.userId || ""),
    { immediate: !!user, deps: [user] }
  );

  // Fetch memories dynamically from backend API
  const { data: memoriesData, refetch: refetchMemories } = useFetch(
    user ? `memory_${user.userId}` : "",
    () => api.memory.list(user?.userId || ""),
    { immediate: !!user, deps: [user] }
  );

  // Fetch career prediction dynamically from backend API
  const { data: careerData } = useFetch(
    user ? `career_${user.userId}` : "",
    () => api.career.predict(user?.userId || ""),
    { immediate: !!user, deps: [user] }
  );

  // Fetch repository architecture analysis dynamically
  const { data: archData, refetch: refetchArch } = useFetch(
    "architecture_analyze",
    () => api.architecture.analyze("demo/payment-platform"),
    { immediate: false }
  );

  // Mutation for simulation initialization
  const { mutate: createSimulationMutate } = useMutation(
    (vars: { scenario: string; difficulty: string }) =>
      api.simulations.create({ scenario: vars.scenario, difficulty: vars.difficulty }),
    {
      onSuccess: (sim) => {
        setSimulationId(sim.id);
        setTranscript([
          { speaker: "AI Monitor", message: `Active War-Room session initialized. Scenario: ${sim.scenario}. Difficulty: ${sim.difficulty || "senior"}` }
        ]);
        setRecoveryScore(25);
        setCompletedActions([]);
        pushActivity(`Incident simulation launched. Connecting telemetric streaming feeds...`);
      }
    }
  );

  // WebSocket subscription for SRE/Security streaming transcripts
  const { connect: connectWS, disconnect: disconnectWS } = useWebSocket({
    onMessage: (event) => {
      if (event.type === "agent" || event.type === "mentor") {
        setTranscript((curr) => [
          ...curr,
          { speaker: event.role || "Mentor", message: event.message || "" }
        ].slice(-8));
      }
      if (event.type === "metric" && event.name === "error_budget_burn") {
        pushActivity(`Alert: error budget burn accelerated to ${event.value}!`);
      }
    }
  });

  useEffect(() => {
    if (simulationId) {
      connectWS(simulationId);
    } else {
      disconnectWS();
    }
    return () => {
      disconnectWS();
    };
  }, [simulationId, connectWS, disconnectWS]);

  const { mutate: evaluateCommandMutate } = useMutation(
    (vars: { command: string; scenario: string }) =>
      api.incidents.evaluateCommand(user?.userId || "demo_user", vars.command, vars.scenario),
    {
      onSuccess: (res, vars) => {
        setTranscript((curr) => [
          ...curr,
          { speaker: "You", message: vars.command },
          { speaker: "AI Mentor", message: res.mentor_feedback }
        ].slice(-8));
        setRecoveryScore(res.recovery_safety);
        refetchTwin();
        refetchMemories();
        pushActivity(`Command evaluated. Diagnosis score: ${res.diagnosis_quality}%. Safety score: ${res.recovery_safety}%`);
      }
    }
  );

  // Spring animation values for numeric gauges
  const animMemoryCount = useAnimatedValue(twinData?.memory_count || 8421, { duration: 800 });
  const animReputationIndex = useAnimatedValue(twinData?.reputation_index || 87, { duration: 800 });

  const activeSimulation = simulations[simulationIndex];

  function jumpTo(section: string) {
    setActiveSection(section);
    document.getElementById(section)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function pushActivity(message: string) {
    setToast(message);
  }

  function startSimulation() {
    const nextIndex = (simulationIndex + 1) % simulations.length;
    setSimulationIndex(nextIndex);
    createSimulationMutate({
      scenario: simulations[nextIndex].title,
      difficulty: "senior"
    });
    jumpTo("simulator");
  }

  function analyzeRepo() {
    setIsAnalyzing(true);
    refetchArch();
    jumpTo("architecture");
    window.setTimeout(() => {
      setIsAnalyzing(false);
      pushActivity("Repository scan complete. ledger.py verified as single point of failure.");
    }, 900);
  }

  function recalculateScores() {
    refetchTwin();
    refetchMemories();
    pushActivity("Digital twin neural indexes re-synchronized.");
  }

  function submitCommand() {
    const cleanCommand = commandText.trim();
    if (!cleanCommand) return;
    evaluateCommandMutate({ command: cleanCommand, scenario: activeSimulation.title });
    setCommandText("");
  }

  function completeRunbookAction(actionId: string, gain: number) {
    if (completedActions.includes(actionId)) return;
    const action = runbookActions.find((item) => item.id === actionId);
    setCompletedActions((current) => [...current, actionId]);
    setRecoveryScore((score) => Math.min(100, score + gain));
    pushActivity(`${action?.label ?? "Action"} completed. Evidentiary telemetry sent to digital twin.`);
  }

  function trackStagePointer(event: ReactPointerEvent<HTMLElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
    
    pointerRef.current = { x, y, active: true };

    const container = event.currentTarget;
    if (!container.classList.contains("tracking")) {
      container.classList.add("tracking");
    }

    const glowEl = container.querySelector(".cursorGlow") as HTMLElement;
    if (glowEl) {
      glowEl.style.transform = `translate3d(${event.clientX - rect.left}px, ${event.clientY - rect.top}px, 0)`;
    }
  }

  // Bind live database-fed values to display arrays, fallback to mock structures
  const liveSkills = twinData?.skill_scores ? twinData.skill_scores.map(s => {
    const matchingStatic = skills.find(sk => sk.name.toLowerCase() === s.domain.toLowerCase());
    return {
      name: s.domain,
      score: s.score,
      color: matchingStatic?.color || "#0d9488",
      icon: matchingStatic?.icon || Code2
    };
  }) : skills;

  const liveReputation = twinData?.reputation ? [
    { label: "Debugging", score: twinData.reputation.debugging, delta: "+7", icon: ServerCrash, color: "#f9735b" },
    { label: "Architecture", score: twinData.reputation.architecture, delta: "+5", icon: Workflow, color: "#3867d6" },
    { label: "Reliability", score: twinData.reputation.reliability, delta: "+9", icon: Gauge, color: "#0d9488" },
    { label: "Leadership", score: twinData.reputation.leadership, delta: "+3", icon: Users, color: "#d99a28" },
    { label: "System Design", score: twinData.reputation.system_design, delta: "+6", icon: Network, color: "#7c4dff" }
  ] : reputation;

  const liveMemories = memoriesData?.memories ? memoriesData.memories.map(m => m.summary) : events;

  const liveCareerSignals = careerData ? [
    { label: "Staff readiness", value: `${careerData.promotion_readiness}%`, detail: careerData.growth_trajectory },
    { label: "Interview readiness", value: `${careerData.interview_readiness}%`, detail: "System design pacing and tradeoff clarity are above bar." },
    { label: "FAANG probability", value: `${careerData.faang_probability}%`, detail: "Improves with security depth and distributed systems storytelling." }
  ] : careerSignals;

  const liveFindings = archData ? [
    ...(archData.findings || []),
    ...(archData.architecture_risks || []),
    ...(archData.security_findings || []),
    ...(archData.scalability_predictions || []),
    ...(archData.dependency_hotspots || []).map(h => `${h} is a blast-radius hotspot across call paths`),
    ...(archData.blast_radius_hotspots || []).map(h => `${h} is a blast-radius hotspot across call paths`)
  ] : repoFindings;

  if (authLoading) {
    return (
      <div className="authLoadingScreen">
        <div className="logoRing">
          <BrainCircuit className="spin" size={32} />
        </div>
        <h2>Synchronizing telemetric session...</h2>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <AuthConsole />;
  }

  return (
    <main className="shell">
      <Sidebar activeSection={activeSection} onSelect={jumpTo} />

      <section className="main">
        {/* Mobile Header */}
        <div className="mobileHeader">
          <div className="brand">
            <div className="brandMark"><BrainCircuit size={24} /></div>
            EngineerOS
          </div>
          <button className="iconButton" type="button" title="Refresh twin" onClick={recalculateScores}><RefreshCcw size={18} /></button>
        </div>

        {/* Topbar */}
        <header className="topbar">
          <div className="titleBlock">
            <div className="eyebrow"><Command size={15} /> AI engineering operating system</div>
            <h1>Engineering Command Center</h1>
            <p>
              A living digital twin that learns from code, incidents, architecture choices, interview simulations,
              and collaboration behavior to accelerate engineering growth.
            </p>
          </div>
          <div className="actions">
            <button className="secondaryButton" type="button" onClick={analyzeRepo}>
              <GitBranch size={18} /> {isAnalyzing ? "Analyzing..." : "Analyze repo"}
            </button>
            <button className="primaryButton" type="button" onClick={startSimulation}><Play size={18} /> Start simulation</button>
          </div>
        </header>

        {/* Hero Grid: Twin Stage + Simulation Panel */}
        <div className="heroGrid">
          <section
            className="twinStage"
            id="twin"
            aria-label="Engineer DNA knowledge graph"
            onPointerMove={trackStagePointer}
            onPointerEnter={trackStagePointer}
            onPointerLeave={(e) => {
              pointerRef.current.active = false;
              e.currentTarget.classList.remove("tracking");
            }}
          >
            <div
              className="cursorGlow"
              style={{ transform: "translate3d(50px, 40px, 0)" }}
            />
            <div className="scanGrid" />
            <TwinGraph pointerRef={pointerRef} />
            <div className="stageOverlay">
              <div className="liveToast"><Sparkles size={15} /> {toast}</div>
              <div className="stageKpis">
                <div><strong>{Math.round(animMemoryCount)}</strong><span>memory nodes</span></div>
                <div><strong>{twinData ? `${twinData.repo_confidence}%` : "94%"}</strong><span>repo signal confidence</span></div>
                <div><strong>{twinData ? `${twinData.experience_simulated_years}y` : "3.8y"}</strong><span>experience simulated</span></div>
                <div><strong>{Math.round(animReputationIndex)}</strong><span>reputation index</span></div>
              </div>
            </div>
          </section>

          <SimulationPanel
            activeSimulation={activeSimulation}
            transcript={transcript}
            commandText={commandText}
            agents={agents}
            onCommandTextChange={setCommandText}
            onSubmitCommand={submitCommand}
          />
        </div>

        {/* Reputation Strip */}
        <ReputationStrip reputation={liveReputation} />

        {/* Content Grid: Skills + Incidents */}
        <div className="contentGrid">
          <SkillGrid
            skills={liveSkills}
            careerSignals={liveCareerSignals}
            isRecalculating={twinLoading}
            onRecalculate={recalculateScores}
          />
          <IncidentBoard
            incidents={incidents}
            runbookActions={runbookActions}
            completedActions={completedActions}
            recoveryScore={recoveryScore}
            onCompleteAction={completeRunbookAction}
          />
        </div>

        {/* Content Grid: Architecture + Memory */}
        <div className="contentGrid">
          <ArchitectureMap
            repoFindings={liveFindings}
            isAnalyzing={isAnalyzing}
            showGraph={showGraph}
            onToggleGraph={() => setShowGraph((value) => !value)}
          />
          <MemoryStream activityFeed={liveMemories} />
        </div>
      </section>
    </main>
  );
}
