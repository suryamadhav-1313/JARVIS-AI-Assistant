import { useEffect, useState } from "react";

// These values are NOT read from real hardware — no OS-level telemetry API
// is wired up in Phase 2. They drift gently for visual life and are clearly
// labeled as simulated so nobody mistakes them for real system data.
function useSimulatedTelemetry() {
  const [values, setValues] = useState({ cpu: 34, ram: 48, battery: 91 });

  useEffect(() => {
    const id = setInterval(() => {
      setValues((prev) => ({
        cpu: clamp(prev.cpu + drift(4), 8, 92),
        ram: clamp(prev.ram + drift(2), 20, 85),
        battery: clamp(prev.battery - Math.random() * 0.05, 0, 100),
      }));
    }, 2200);
    return () => clearInterval(id);
  }, []);

  return values;
}

function drift(range) {
  return (Math.random() - 0.5) * range;
}
function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function Meter({ label, value }) {
  return (
    <div className="stat-row-wrap" style={{ marginBottom: 8 }}>
      <div className="stat-row">
        <span className="label">{label}</span>
        <span className="value">{Math.round(value)}%</span>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default function SystemStatus({ systemOnline, voiceActive }) {
  const { cpu, ram, battery } = useSimulatedTelemetry();

  return (
    <div className="hud-panel">
      <div className="panel-title">SYSTEM STATUS</div>
      <Meter label="CPU" value={cpu} />
      <Meter label="RAM" value={ram} />
      <Meter label="BATTERY" value={battery} />

      <div className="stat-row">
        <span className="label">SYSTEM</span>
        <span className="value" style={{ color: systemOnline ? "var(--green)" : "var(--red)" }}>
          {systemOnline === null ? "CHECKING" : systemOnline ? "ONLINE" : "OFFLINE"}
        </span>
      </div>
      <div className="stat-row">
        <span className="label">VOICE</span>
        <span className="value">{voiceActive ? "LISTENING" : "STANDBY"}</span>
      </div>
      <div className="stat-row">
        <span className="label">AI CORE</span>
        <span className="value">{systemOnline ? "ACTIVE" : "OFFLINE"}</span>
      </div>
      <div className="stat-row">
        <span className="label">TOOLS</span>
        <span className="value">{systemOnline ? "READY" : "OFFLINE"}</span>
      </div>

      <div className="simulated-tag">CPU / RAM / BATTERY: SIMULATED UI TELEMETRY</div>
    </div>
  );
}
