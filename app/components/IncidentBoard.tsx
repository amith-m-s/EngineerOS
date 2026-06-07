"use client";

import { CheckCircle2, CircleAlert } from "lucide-react";

type Incident = {
  name: string;
  detail: string;
  time: string;
  severity: string;
};

type RunbookAction = {
  id: string;
  label: string;
  detail: string;
  gain: number;
};

export default function IncidentBoard({
  incidents,
  runbookActions,
  completedActions,
  recoveryScore,
  onCompleteAction
}: {
  incidents: Incident[];
  runbookActions: RunbookAction[];
  completedActions: string[];
  recoveryScore: number;
  onCompleteAction: (actionId: string, gain: number) => void;
}) {
  const resolvedCount = completedActions.length;

  return (
    <aside className="panel section" id="incidents">
      <div className="sectionTitle">
        <h2>Production Incidents</h2>
        <span className="statusPill">{resolvedCount}/4 actions</span>
      </div>
      <div className="recoveryMeter">
        <div>
          <span>Recovery quality</span>
          <strong>{recoveryScore}%</strong>
        </div>
        <div className="bar"><span style={{ width: `${recoveryScore}%`, background: recoveryScore > 74 ? "#00ffcc" : "#ff4d6a" }} /></div>
      </div>
      <div className="incidentBoard">
        {incidents.map((incident) => (
          <article className="incident" key={incident.name}>
            <span className="severity" style={{ background: incident.severity }} />
            <div>
              <h3>{incident.name}</h3>
              <p>{incident.detail}</p>
            </div>
            <div className="timer">{incident.time}</div>
          </article>
        ))}
      </div>
      <div className="runbook">
        {runbookActions.map((action) => {
          const isDone = completedActions.includes(action.id);
          return (
            <button
              className={isDone ? "runbookAction done" : "runbookAction"}
              key={action.id}
              type="button"
              onClick={() => onCompleteAction(action.id, action.gain)}
            >
              {isDone ? <CheckCircle2 size={16} /> : <CircleAlert size={16} />}
              <span>
                <strong>{action.label}</strong>
                <em>{action.detail}</em>
              </span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
