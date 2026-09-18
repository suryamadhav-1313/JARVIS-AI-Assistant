// hooks/useJarvisState.js
import { useCallback, useEffect, useRef, useState } from "react";
import { checkHealth, sendCommand } from "../services/jarvisApi";

const MAX_LOG_ENTRIES = 30;

function timestamp() {
  const d = new Date();
  return d.toTimeString().slice(0, 8);
}

export function useJarvisState() {
  const [booted, setBooted] = useState(false);
  const [systemOnline, setSystemOnline] = useState(null); // null = unknown, checking
  const [currentCommand, setCurrentCommand] = useState("");
  const [commandStatus, setCommandStatus] = useState("idle"); // idle | sending | success | error
  const [activityLog, setActivityLog] = useState([
    { time: timestamp(), text: "INTERFACE READY", tone: "ok" },
  ]);
  const [voiceActive, setVoiceActive] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  const pollRef = useRef(null);

  const pushLog = useCallback((text, tone = "info") => {
    setActivityLog((prev) => {
      const next = [...prev, { time: timestamp(), text, tone }];
      return next.slice(-MAX_LOG_ENTRIES);
    });
  }, []);

  const pingHealth = useCallback(async () => {
    const result = await checkHealth();
    setSystemOnline(result.online);
    return result;
  }, []);

  useEffect(() => {
    pingHealth();
    pollRef.current = setInterval(pingHealth, 15000);
    return () => clearInterval(pollRef.current);
  }, [pingHealth]);

  const submitCommand = useCallback(
    async (command) => {
      const trimmed = (command || "").trim();
      if (!trimmed) return;

      setCurrentCommand(trimmed);
      setCommandStatus("sending");
      pushLog(`COMMAND RECEIVED: ${trimmed.toUpperCase()}`, "info");

      const result = await sendCommand(trimmed);

      if (result.ok) {
        setCommandStatus("success");
        setSystemOnline(true);
        pushLog("ACTION COMPLETED", "ok");
      } else {
        setCommandStatus("error");
        if (result.error === "UNREACHABLE" || result.error === "TIMEOUT") {
          setSystemOnline(false);
        }
        pushLog(`COMMAND FAILED: ${result.error || "UNKNOWN ERROR"}`, "error");
      }

      setTimeout(() => setCommandStatus("idle"), 2200);
      return result;
    },
    [pushLog]
  );

  const completeBoot = useCallback(() => {
    setBooted(true);
    pushLog("J.A.R.V.I.S. ONLINE", "ok");
  }, [pushLog]);

  return {
    booted,
    completeBoot,
    systemOnline,
    pingHealth,
    currentCommand,
    commandStatus,
    submitCommand,
    activityLog,
    pushLog,
    voiceActive,
    setVoiceActive,
    audioLevel,
    setAudioLevel,
  };
}
