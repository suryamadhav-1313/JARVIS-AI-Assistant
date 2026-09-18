export default function ActivityLog({ entries }) {
  return (
    <div className="hud-panel" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
      <div className="panel-title">ACTIVITY LOG</div>
      <div className="log-list">
        {entries
          .slice()
          .reverse()
          .map((e, i) => (
            <div key={i} className={`log-entry ${e.tone}`}>
              <span className="t">[{e.time}]</span>
              <span className="msg">{e.text}</span>
            </div>
          ))}
      </div>
    </div>
  );
}
