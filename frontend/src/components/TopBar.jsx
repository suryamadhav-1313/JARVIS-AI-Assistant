import { useEffect, useState } from "react";

function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

const DAYS = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"];
const MONTHS = [
  "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
  "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
];

export default function TopBar({ systemOnline, voiceActive }) {
  const now = useClock();
  const time = now.toTimeString().slice(0, 8);
  const date = `${DAYS[now.getDay()]}, ${now.getDate()} ${MONTHS[now.getMonth()]} ${now.getFullYear()}`;

  return (
    <div className="hud-topbar">
      <div className="hud-brand">
        <div className="title">J.A.R.V.I.S.</div>
        <div className="subtitle">JUST A RATHER VERY INTELLIGENT SYSTEM</div>
        <div className="brand-rule" />
      </div>

      <div className="hud-clock">
        <div className="time">{time}</div>
        <div className="date">{date}</div>
      </div>

      <div className="hud-status">
        <div className="online-row">
          <span
            className={`dot ${systemOnline === null ? "pending" : systemOnline ? "on" : "off"}`}
          />
          SYSTEM {systemOnline === null ? "CHECKING" : systemOnline ? "ONLINE" : "OFFLINE"}
        </div>
        <div className="hud-indicators">
          <span className="indicator">
            <span className={`dot ${systemOnline ? "on" : "off"}`} /> AI CORE
          </span>
          <span className="indicator">
            <span className={`dot ${voiceActive ? "on" : "off"}`} /> VOICE
          </span>
          <span className="indicator">
            <span className={`dot ${systemOnline ? "on" : "off"}`} /> TOOLS
          </span>
          <span className="indicator">
            <span className={`dot ${systemOnline ? "on" : "off"}`} /> NETWORK
          </span>
        </div>
      </div>
    </div>
  );
}
