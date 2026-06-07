"use client";

import { Sparkles } from "lucide-react";

export default function MemoryStream({ activityFeed }: { activityFeed: string[] }) {
  return (
    <aside className="panel section" id="agents">
      <div className="sectionTitle">
        <h2>Long-Term Memory</h2>
        <span className="statusPill">Synced</span>
      </div>
      <div className="activity">
        {activityFeed.map((event) => (
          <div className="event" key={event}>
            <div className="eventIcon"><Sparkles size={15} /></div>
            <p><strong>Memory update:</strong> {event}</p>
          </div>
        ))}
      </div>
    </aside>
  );
}
