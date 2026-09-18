import { motion } from "framer-motion";

const NODES = [
  { label: "SYSTEM", angle: 200 },
  { label: "MEDIA", angle: 235 },
  { label: "TOOLS", angle: 270 },
  { label: "CODES", angle: 305 },
  { label: "FILES", angle: 340 },
  { label: "AI CHAT", angle: 20 },
  { label: "BROWSER", angle: 55 },
  { label: "NOTES", angle: 90 },
  { label: "CALENDAR", angle: 125 },
  { label: "SETTINGS", angle: 160 },
];

const RADIUS_PCT = 46;

export default function RadialMenu({ onSelect }) {
  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
      <svg
        viewBox="0 0 100 100"
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}
      >
        {NODES.map((n, i) => {
          const rad = (n.angle * Math.PI) / 180;
          const x = 50 + Math.cos(rad) * RADIUS_PCT;
          const y = 50 + Math.sin(rad) * RADIUS_PCT;
          return (
            <line
              key={i}
              x1="50"
              y1="50"
              x2={x}
              y2={y}
              stroke="rgba(95,227,255,0.12)"
              strokeWidth="0.15"
            />
          );
        })}
      </svg>

      {NODES.map((n, i) => {
        const rad = (n.angle * Math.PI) / 180;
        const left = 50 + Math.cos(rad) * RADIUS_PCT;
        const top = 50 + Math.sin(rad) * RADIUS_PCT;
        const labelOnLeft = Math.cos(rad) < -0.15;
        return (
          <motion.button
            key={n.label}
            type="button"
            className="radial-node"
            style={{
              left: `${left}%`,
              top: `${top}%`,
              flexDirection: labelOnLeft ? "row-reverse" : "row",
              pointerEvents: "auto",
              background: "none",
              border: "none",
              padding: 4,
            }}
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.05 * i, duration: 0.4 }}
            onClick={() => onSelect?.(n.label)}
          >
            <span className="node-dot" />
            <span className="node-label">{n.label}</span>
          </motion.button>
        );
      })}
    </div>
  );
}
