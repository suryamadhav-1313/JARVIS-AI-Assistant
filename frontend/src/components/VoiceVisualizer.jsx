import { useEffect, useRef } from "react";

const BAR_COUNT = 48;

export default function VoiceVisualizer({ level = 0, bins = null, active = false }) {
  const canvasRef = useRef(null);
  const rafRef = useRef(null);
  const phaseRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      const gap = w / BAR_COUNT;
      phaseRef.current += 0.05;

      for (let i = 0; i < BAR_COUNT; i++) {
        let amp;
        if (active && bins && bins.length) {
          const binIndex = Math.floor((i / BAR_COUNT) * bins.length);
          amp = bins[binIndex] / 255;
        } else {
          // idle animation: gentle sine sweep
          amp = 0.15 + 0.12 * Math.sin(phaseRef.current + i * 0.35);
        }
        const barH = Math.max(2, amp * h * 0.85);
        const x = i * gap + gap * 0.2;
        const y = h / 2 - barH / 2;

        ctx.fillStyle = active
          ? `rgba(95, 227, 255, ${0.4 + amp * 0.6})`
          : "rgba(95, 227, 255, 0.35)";
        ctx.fillRect(x, y, gap * 0.6, barH);
      }

      rafRef.current = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [active, bins]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: "100%", height: "54px", display: "block" }}
      aria-label="Voice amplitude waveform"
    />
  );
}
