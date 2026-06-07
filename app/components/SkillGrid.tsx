"use client";

import type { LucideIcon } from "lucide-react";
import { RefreshCcw } from "lucide-react";

type Skill = {
  name: string;
  score: number;
  color: string;
  icon: LucideIcon;
};

type CareerSignal = {
  label: string;
  value: string;
  detail: string;
};

export default function SkillGrid({
  skills,
  careerSignals,
  isRecalculating,
  onRecalculate
}: {
  skills: Skill[];
  careerSignals: CareerSignal[];
  isRecalculating: boolean;
  onRecalculate: () => void;
}) {
  return (
    <section className="panel section" id="career">
      <div className="sectionTitle">
        <h2>Engineering Skill Graph</h2>
        <button className="iconButton" type="button" title="Recalculate scores" onClick={onRecalculate}>
          <RefreshCcw className={isRecalculating ? "spin" : ""} size={17} />
        </button>
      </div>
      <div className="skillGrid">
        {skills.map((skill) => (
          <article className="skillTile" key={skill.name}>
            <header>
              <h3>{skill.name}</h3>
              <skill.icon size={18} color={skill.color} />
            </header>
            <div>
              <div className="score">{skill.score}</div>
              <div className="bar"><span style={{ width: `${skill.score}%`, background: skill.color }} /></div>
            </div>
          </article>
        ))}
      </div>
      <div className="careerGrid">
        {careerSignals.map((signal) => (
          <article className="careerSignal" key={signal.label}>
            <span>{signal.label}</span>
            <strong>{signal.value}</strong>
            <p>{signal.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
