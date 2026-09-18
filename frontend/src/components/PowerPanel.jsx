import { useEffect, useState } from "react";

const BLOCKS = 20;

export default function PowerPanel() {
  const [power, setPower] = useState(98);

  useEffect(() => {
    const id = setInterval(() => {
      setPower((p) => {
        const next = p - Math.random() * 0.03;
        return next < 60 ? 98 : next;
      });
    }, 3000);
    return () => clearInterval(id);
  }, []);

  const filled = Math.round((power / 100) * BLOCKS);

  return (
    <div className="hud-panel">
      <div className="panel-title">POWER LEVEL</div>
      <div style={{ fontSize: 10, letterSpacing: 1.5, color: "var(--text-dim)", marginBottom: 6 }}>
        JARVIS CORE
      </div>
      <div style={{ display: "flex", gap: 2, marginBottom: 6 }}>
        {Array.from({ length: BLOCKS }, (_, i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 14,
              background: i < filled ? "var(--cyan)" : "rgba(95,227,255,0.12)",
              boxShadow: i < filled ? "0 0 6px var(--cyan-glow)" : "none",
            }}
          />
        ))}
      </div>
      <div style={{ fontFamily: "var(--font-display)", fontSize: 16, color: "var(--cyan)" }}>
        {power.toFixed(0)}%
      </div>
      <div className="simulated-tag">SIMULATED UI TELEMETRY</div>
    </div>
  );
}
