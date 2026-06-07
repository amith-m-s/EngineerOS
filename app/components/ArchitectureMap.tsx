"use client";

import {
  ArrowRight,
  BrainCircuit,
  Database,
  Flame,
  GitBranch,
  Lock,
  Network,
  Route,
  ShieldAlert
} from "lucide-react";

export default function ArchitectureMap({
  repoFindings,
  isAnalyzing,
  showGraph,
  onToggleGraph
}: {
  repoFindings: string[];
  isAnalyzing: boolean;
  showGraph: boolean;
  onToggleGraph: () => void;
}) {
  return (
    <section className="panel section" id="architecture">
      <div className="sectionTitle">
        <h2>Architecture Intelligence</h2>
        <button className="secondaryButton" type="button" onClick={onToggleGraph}>
          <Network size={17} /> {showGraph ? "Close graph" : "Open graph"}
        </button>
      </div>
      <div className="repoInsights">
        <div className="insight" style={{ background: "linear-gradient(135deg, #0d9488, #0f766e)" }}><strong>42</strong><span>critical dependencies mapped</span></div>
        <div className="insight" style={{ background: "linear-gradient(135deg, #3867d6, #2d52a8)" }}><strong>11</strong><span>scaling constraints predicted</span></div>
        <div className="insight" style={{ background: "linear-gradient(135deg, #f9735b, #e05540)" }}><strong>6</strong><span>security risks need review</span></div>
      </div>
      <div className={isAnalyzing ? "analysisPipeline running" : "analysisPipeline"}>
        <span><GitBranch size={15} /> clone graph</span>
        <ArrowRight size={15} />
        <span><Database size={15} /> map deps</span>
        <ArrowRight size={15} />
        <span><Lock size={15} /> threat scan</span>
        <ArrowRight size={15} />
        <span><BrainCircuit size={15} /> score DNA</span>
      </div>
      {showGraph && (
        <div className="architectureMap" aria-label="Repository dependency graph">
          <div className="mapNode core"><Database size={18} /> Postgres</div>
          <div className="mapNode api"><Route size={18} /> FastAPI</div>
          <div className="mapNode memory"><BrainCircuit size={18} /> Twin Memory</div>
          <div className="mapNode risk"><Flame size={18} /> Hotspot</div>
          <div className="mapLine one" />
          <div className="mapLine two" />
          <div className="mapLine three" />
        </div>
      )}
      <div className="findingList">
        {repoFindings.map((finding) => (
          <div className="finding" key={finding}><ShieldAlert size={15} /> {finding}</div>
        ))}
      </div>
    </section>
  );
}
