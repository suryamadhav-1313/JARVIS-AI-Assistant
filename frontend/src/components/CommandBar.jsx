import { useState } from "react";
import { Mic, MicOff, Send } from "lucide-react";

export default function CommandBar({ onSubmit, status, voiceActive, onToggleVoice }) {
  const [text, setText] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit(text);
    setText("");
  }

  const statusLabel =
    status === "sending"
      ? "COMMAND SENT — PROCESSING"
      : status === "success"
      ? "SUCCESS"
      : status === "error"
      ? "ERROR"
      : "";

  return (
    <form className="command-bar" onSubmit={handleSubmit}>
      <button
        type="button"
        className={`mic-btn ${voiceActive ? "active" : ""}`}
        onClick={onToggleVoice}
        aria-pressed={voiceActive}
        aria-label="Toggle microphone"
      >
        {voiceActive ? <Mic size={15} /> : <MicOff size={15} />}
      </button>
      <input
        type="text"
        placeholder="ENTER COMMAND..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        aria-label="JARVIS command input"
      />
      <span className={`command-status ${status}`}>{statusLabel}</span>
      <button type="submit" className="mic-btn" aria-label="Send command">
        <Send size={14} />
      </button>
    </form>
  );
}
