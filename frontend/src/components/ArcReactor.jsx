import { Suspense, useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import ReactorRings from "./ReactorRings";
import ReactorParticles from "./ReactorParticles";

function useReducedMotion() {
  const [reduced, setReduced] = useState(
    () =>
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handler = (e) => setReduced(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);
  return reduced;
}

export default function ArcReactor({ audioLevel = 0 }) {
  const reducedMotion = useReducedMotion();

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <Canvas
        orthographic
        camera={{ zoom: 110, position: [0, 0, 10] }}
        gl={{ antialias: true, alpha: true }}
        dpr={[1, 1.5]}
      >
        <Suspense fallback={null}>
          <ReactorRings audioLevel={audioLevel} reducedMotion={reducedMotion} />
          <ReactorParticles audioLevel={audioLevel} reducedMotion={reducedMotion} />
        </Suspense>
      </Canvas>
    </div>
  );
}
