// hooks/useVoiceInput.js
// Phase 2 scope: exposes microphone on/off state tied to useAudioAnalyzer.
// Deliberately does NOT implement wake-word detection, continuous listening,
// or speech-to-text — that belongs to a later phase.
import { useCallback, useState } from "react";
import { useAudioAnalyzer } from "./useAudioAnalyzer";

export function useVoiceInput() {
  const [active, setActive] = useState(false);
  const analyzer = useAudioAnalyzer();

  const toggle = useCallback(async () => {
    if (active) {
      analyzer.stop();
      setActive(false);
      return;
    }
    const ok = await analyzer.start();
    setActive(ok);
  }, [active, analyzer]);

  return {
    active,
    toggle,
    level: analyzer.level,
    bins: analyzer.bins,
    permission: analyzer.permission,
  };
}
