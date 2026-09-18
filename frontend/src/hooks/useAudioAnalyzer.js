// hooks/useAudioAnalyzer.js
// Wraps the Web Audio API to expose a smoothed 0..1 amplitude level and a
// small frequency-bin snapshot for waveform rendering. Never throws if the
// microphone is unavailable or denied — callers fall back to idle animation.
import { useCallback, useEffect, useRef, useState } from "react";

const FFT_SIZE = 256;
const SMOOTHING = 0.35;

export function useAudioAnalyzer() {
  const [level, setLevel] = useState(0);
  const [bins, setBins] = useState(() => new Uint8Array(FFT_SIZE / 2));
  const [permission, setPermission] = useState("idle"); // idle | granted | denied | unsupported

  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const rafRef = useRef(null);
  const smoothedRef = useRef(0);

  const stop = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close().catch(() => {});
      audioCtxRef.current = null;
    }
    analyserRef.current = null;
    smoothedRef.current = 0;
    setLevel(0);
  }, []);

  const start = useCallback(async () => {
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setPermission("unsupported");
      return false;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = FFT_SIZE;
      source.connect(analyser);

      audioCtxRef.current = ctx;
      analyserRef.current = analyser;
      setPermission("granted");

      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) sum += data[i];
        const avg = sum / data.length / 255; // 0..1
        smoothedRef.current = smoothedRef.current * SMOOTHING + avg * (1 - SMOOTHING);
        setLevel(smoothedRef.current);
        setBins(data.slice());
        rafRef.current = requestAnimationFrame(tick);
      };
      tick();
      return true;
    } catch (err) {
      setPermission("denied");
      return false;
    }
  }, []);

  useEffect(() => stop, [stop]);

  return { level, bins, permission, start, stop };
}
