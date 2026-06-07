"use client";

import { BrainCircuit, LogOut } from "lucide-react";
import { useAuth } from "../hooks";

const sections = [
  { id: "twin", label: "Digital Twin", icon: BrainCircuit },
  { id: "simulator", label: "Simulator", icon: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg> },
  { id: "agents", label: "Agents", icon: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg> },
  { id: "incidents", label: "Incidents", icon: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg> },
  { id: "architecture", label: "Architecture", icon: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/></svg> },
  { id: "career", label: "Career", icon: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/><path d="M12 18h.01"/><path d="M17.99 11.66A6 6 0 0 1 15.77 16.67"/><circle cx="12" cy="12" r="2"/></svg> }
] as const;

export default function Sidebar({
  activeSection,
  onSelect
}: {
  activeSection: string;
  onSelect: (section: string) => void;
}) {
  const { user, logout } = useAuth();
  const userInitial = user?.email ? user.email.charAt(0).toUpperCase() : "D";
  const userDisplayEmail = user?.email || "demo@engineeros.io";

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brandMark"><BrainCircuit size={22} /></div>
        EngineerOS
      </div>
      <nav className="nav" aria-label="EngineerOS modules">
        {sections.map((item) => (
          <button
            className={activeSection === item.id ? "active" : ""}
            key={item.label}
            type="button"
            title={item.label}
            onClick={() => onSelect(item.id)}
          >
            <item.icon size={18} />
            {item.label}
          </button>
        ))}
      </nav>

      {user && (
        <div className="sidebarUserProfile">
          <div className="userAvatar">{userInitial}</div>
          <div className="userInfo">
            <span className="userEmail" title={userDisplayEmail}>{userDisplayEmail}</span>
            <span className="userRole">Senior Engineer</span>
          </div>
          <button className="signOutBtn" type="button" title="Sign Out" onClick={logout}>
            <LogOut size={16} />
          </button>
        </div>
      )}

      <div className="sidebarFooter">
        Live twin sync: Neo4j, Qdrant, PostgreSQL, Kafka, Redis, and agent memory streams.
        <div className="statusDots">
          <span className="statusDot active" title="API Status: Connected" />
          <span className="statusDot active" title="Database Sync: Active" />
          <span className="statusDot active" title="Memory Stream: Listening" />
        </div>
      </div>
    </aside>
  );
}
