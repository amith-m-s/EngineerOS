"use client";

import { Bot, Send, TerminalSquare, Users, Zap } from "lucide-react";

type Agent = {
  role: string;
  stance: string;
  color: string;
};

type Simulation = {
  title: string;
  detail: string;
  pressure: string;
  clock: string;
};

type TranscriptTurn = {
  speaker: string;
  message: string;
};

export default function SimulationPanel({
  activeSimulation,
  transcript,
  commandText,
  agents,
  onCommandTextChange,
  onSubmitCommand
}: {
  activeSimulation: Simulation;
  transcript: TranscriptTurn[];
  commandText: string;
  agents: Agent[];
  onCommandTextChange: (value: string) => void;
  onSubmitCommand: () => void;
}) {
  return (
    <aside className="panel commandPanel" id="simulator">
      <div className="panelHeader">
        <h2>Active Simulation</h2>
        <span className="statusPill">{activeSimulation.pressure} / {activeSimulation.clock}</span>
      </div>
      <div className="scenario">
        <div className="scenarioIcon"><Zap size={22} /></div>
        <div>
          <h3>{activeSimulation.title}</h3>
          <p>{activeSimulation.detail}</p>
        </div>
      </div>
      <div className="missionConsole">
        <div><TerminalSquare size={16} /> live objective</div>
        <code>diagnose --blast-radius --rollback-plan --stakeholder-brief</code>
      </div>
      <div className="warRoom">
        <div className="warRoomHeader">
          <span><Users size={16} /> Agent war room</span>
          <strong>{transcript.length} turns</strong>
        </div>
        <div className="transcript">
          {transcript.map((turn, index) => (
            <div className={turn.speaker === "You" ? "turn you" : "turn"} key={`${turn.speaker}-${index}`}>
              <strong>{turn.speaker}</strong>
              <p>{turn.message}</p>
            </div>
          ))}
        </div>
        <div className="commandInput">
          <input
            aria-label="Incident command"
            value={commandText}
            onChange={(event) => onCommandTextChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onSubmitCommand();
            }}
          />
          <button className="iconButton" type="button" title="Send command" onClick={onSubmitCommand}>
            <Send size={17} />
          </button>
        </div>
      </div>
      <div className="agentList">
        {agents.map((agent) => (
          <div className="agentRow" key={agent.role}>
            <div className="agentAvatar" style={{ background: agent.color }}>
              <Bot size={16} />
            </div>
            <div>
              <strong>{agent.role}</strong>
              <span>{agent.stance}</span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
