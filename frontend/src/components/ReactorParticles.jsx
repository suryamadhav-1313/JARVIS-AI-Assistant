import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export default function ReactorParticles({ count = 90, audioLevel = 0, reducedMotion = false }) {
  const pointsRef = useRef();

  const { positions, radii, speeds, angles } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const radii = new Float32Array(count);
    const speeds = new Float32Array(count);
    const angles = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      const r = 2.2 + Math.random() * 1.3;
      const a = Math.random() * Math.PI * 2;
      const y = (Math.random() - 0.5) * 0.6;
      radii[i] = r;
      angles[i] = a;
      speeds[i] = 0.03 + Math.random() * 0.06;
      positions[i * 3] = Math.cos(a) * r;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = Math.sin(a) * r;
    }
    return { positions, radii, speeds, angles };
  }, [count]);

  useFrame((_, delta) => {
    if (!pointsRef.current) return;
    const posAttr = pointsRef.current.geometry.attributes.position;
    const speedScale = reducedMotion ? 0.2 : 1;
    for (let i = 0; i < count; i++) {
      angles[i] += speeds[i] * delta * speedScale * (1 + audioLevel * 0.4);
      const r = radii[i];
      posAttr.array[i * 3] = Math.cos(angles[i]) * r;
      posAttr.array[i * 3 + 2] = Math.sin(angles[i]) * r;
    }
    posAttr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef} rotation={[Math.PI / 2, 0, 0]}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color={new THREE.Color("#5fe3ff")}
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
}
