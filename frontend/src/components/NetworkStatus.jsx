import { useEffect, useState } from "react";
import { JARVIS_API_BASE_URL } from "../services/jarvisApi";

// LATENCY here is a real measurement (round-trip to the backend's /health
// endpoint), not a simulated number. If the backend is unreachable we show
// DATA UNAVAILABLE rather than inventing a figure.
export default function NetworkStatus({ systemOnline }) {
  const [latencyMs, setLatencyMs] = useState(null);
  const [browserOnline, setBrowserOnline] = useState(
    typeof navigator !== "undefined" ? navigator.onLine : true
  );

  useEffect(() => {
    const goOnline = () => setBrowserOnline(true);
    const goOffline = () => setBrowserOnline(false);
    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function probe() {
      const start = performance.now();
      try {
        const res = await fetch(`${JARVIS_API_BASE_URL}/health`, { method: "GET" });
        const elapsed = performance.now() - start;
        if (!cancelled) setLatencyMs(res.ok ? Math.round(elapsed) : null);
      } catch {
        if (!cancelled) setLatencyMs(null);
      }
    }
    probe();
    const id = setInterval(probe, 10000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="hud-panel">
      <div className="panel-title">NETWORK STATUS</div>
      <div className="stat-row">
        <span className="label">NETWORK</span>
        <span className="value">{browserOnline ? "CONNECTED" : "DISCONNECTED"}</span>
      </div>
      <div className="stat-row">
        <span className="label">CONNECTION</span>
        <span className="value" style={{ color: systemOnline ? "var(--green)" : "var(--red)" }}>
          {systemOnline === null ? "CHECKING" : systemOnline ? "SECURE" : "LOST"}
        </span>
      </div>
      <div className="stat-row">
        <span className="label">LATENCY</span>
        <span className="value">{latencyMs !== null ? `${latencyMs} MS` : "DATA UNAVAILABLE"}</span>
      </div>
      <div className="stat-row">
        <span className="label">STATUS</span>
        <span className="value">{systemOnline ? "ONLINE" : "DATA UNAVAILABLE"}</span>
      </div>
    </div>
  );
}
