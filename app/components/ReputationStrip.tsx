"use client";

import type { LucideIcon } from "lucide-react";
import { Cpu } from "lucide-react";

type ReputationItem = {
  label: string;
  score: number;
  delta: string;
  icon: LucideIcon;
  color: string;
};

export default function ReputationStrip({ reputation }: { reputation: ReputationItem[] }) {
  return (
    <section className="osStrip" aria-label="EngineerOS live reputation and data plane">
      {reputation.map((item) => (
        <article className="reputationTile" key={item.label}>
          <div className="repIcon" style={{ color: item.color }}><item.icon size={18} /></div>
          <div>
            <span>{item.label}</span>
            <strong>{item.score}</strong>
          </div>
          <em>{item.delta}</em>
        </article>
      ))}
      <article className="dataPlane">
        <div><Cpu size={18} /> Evidence pipeline</div>
        <span>Git commits · incident turns · architecture ADRs · Neo4j DNA · Qdrant memory · reputation scores</span>
      </article>
    </section>
  );
}
