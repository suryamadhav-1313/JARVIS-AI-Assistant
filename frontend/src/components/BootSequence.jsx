import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const LINES = [
  "INITIALIZING J.A.R.V.I.S...",
  "SYSTEM CHECK ........ OK",
  "AI CORE ............ OK",
  "VOICE MODULE ....... READY",
  "MEMORY ............. READY",
  "TOOLS .............. ONLINE",
  "INTERFACE .......... READY",
  "J.A.R.V.I.S. ONLINE",
];

const LINE_DELAY_MS = 260;

export default function BootSequence({ onComplete }) {
  const [visibleCount, setVisibleCount] = useState(0);
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    if (visibleCount >= LINES.length) {
      const t = setTimeout(finish, 500);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setVisibleCount((c) => c + 1), LINE_DELAY_MS);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visibleCount]);

  function finish() {
    if (exiting) return;
    setExiting(true);
    setTimeout(() => onComplete?.(), 400);
  }

  useEffect(() => {
    const handler = () => finish();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exiting]);

  return (
    <AnimatePresence>
      {!exiting && (
        <motion.div
          className="boot-screen"
          onClick={finish}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          <motion.div
            className="boot-title"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            J.A.R.V.I.S.
          </motion.div>
          <div>
            {LINES.slice(0, visibleCount).map((line, i) => {
              const isOk = /OK|READY|ONLINE/.test(line);
              const [main, tag] = isOk ? splitTag(line) : [line, null];
              return (
                <motion.div
                  key={i}
                  className="boot-line"
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  {main}
                  {tag && <span className="ok-tag">{tag}</span>}
                </motion.div>
              );
            })}
          </div>
          <div className="boot-skip">PRESS ANY KEY OR CLICK TO SKIP</div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function splitTag(line) {
  const match = line.match(/(OK|READY|ONLINE)$/);
  if (!match) return [line, null];
  return [line.slice(0, match.index), match[0]];
}
