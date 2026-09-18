import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const CYAN = new THREE.Color("#5fe3ff");
const CYAN_DIM = new THREE.Color("#1c6a86");

/** Thin circular ring built from a torus, flattened. */
function RingLine({ radius, thickness = 0.02, color = CYAN, opacity = 0.8, segments = 128 }) {
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[radius, thickness, 8, segments]} />
      <meshBasicMaterial color={color} transparent opacity={opacity} />
    </mesh>
  );
}

/** Ring made of discrete segments (dashes) around the circle, for the "segmented outer ring". */
function SegmentedRing({ radius, count = 36, arcFraction = 0.55, thickness = 0.05, color = CYAN }) {
  const segments = useMemo(() => {
    const arr = [];
    const gapAngle = (Math.PI * 2) / count;
    for (let i = 0; i < count; i++) {
      arr.push(i * gapAngle);
    }
    return arr;
  }, [count]);

  return (
    <group rotation={[Math.PI / 2, 0, 0]}>
      {segments.map((angle, i) => (
        <mesh key={i} rotation={[0, 0, angle]}>
          <torusGeometry
            args={[radius, thickness, 4, 8, gapArc(count, arcFraction)]}
          />
          <meshBasicMaterial color={color} transparent opacity={0.85} />
        </mesh>
      ))}
    </group>
  );
}

function gapArc(count, arcFraction) {
  return ((Math.PI * 2) / count) * arcFraction;
}

/** Radial tick marks around a circle - "technical markings". */
function TickMarks({ radius, count = 60, length = 0.06, color = CYAN_DIM }) {
  const group = useRef();
  const marks = useMemo(() => {
    const arr = [];
    for (let i = 0; i < count; i++) {
      const long = i % 5 === 0;
      arr.push({ angle: (i / count) * Math.PI * 2, long });
    }
    return arr;
  }, [count]);

  return (
    <group ref={group} rotation={[Math.PI / 2, 0, 0]}>
      {marks.map((m, i) => (
        <mesh
          key={i}
          position={[Math.cos(m.angle) * radius, Math.sin(m.angle) * radius, 0]}
          rotation={[0, 0, m.angle]}
        >
          <planeGeometry args={[m.long ? length * 1.8 : length, 0.012]} />
          <meshBasicMaterial color={color} transparent opacity={m.long ? 0.9 : 0.5} />
        </mesh>
      ))}
    </group>
  );
}

/** Small orbiting nodes on a ring. */
function RingNodes({ radius, count = 8, color = CYAN }) {
  const nodes = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => (i / count) * Math.PI * 2),
    [count]
  );
  return (
    <group rotation={[Math.PI / 2, 0, 0]}>
      {nodes.map((angle, i) => (
        <mesh key={i} position={[Math.cos(angle) * radius, Math.sin(angle) * radius, 0]}>
          <circleGeometry args={[0.035, 16]} />
          <meshBasicMaterial color={color} transparent opacity={0.9} />
        </mesh>
      ))}
    </group>
  );
}

export default function ReactorRings({ audioLevel = 0, reducedMotion = false }) {
  const innerRef = useRef();
  const middleRef = useRef();
  const outerRef = useRef();
  const scanRef = useRef();
  const coreRef = useRef();
  const nodesRef = useRef();

  useFrame((state, delta) => {
    const speedScale = reducedMotion ? 0.25 : 1;
    const boost = 1 + audioLevel * 0.6;

    if (innerRef.current) innerRef.current.rotation.z += delta * 0.35 * speedScale * boost;
    if (middleRef.current) middleRef.current.rotation.z -= delta * 0.2 * speedScale * boost;
    if (outerRef.current) outerRef.current.rotation.z += delta * 0.09 * speedScale;
    if (nodesRef.current) nodesRef.current.rotation.z -= delta * 0.14 * speedScale;
    if (scanRef.current) scanRef.current.rotation.z += delta * 0.9 * speedScale;

    if (coreRef.current) {
      const t = state.clock.elapsedTime;
      const breathe = 1 + Math.sin(t * 1.6) * 0.035 + audioLevel * 0.18;
      coreRef.current.scale.setScalar(breathe);
      const mat = coreRef.current.material;
      if (mat) mat.opacity = 0.65 + Math.sin(t * 1.6) * 0.15 + audioLevel * 0.25;
    }
  });

  return (
    <group>
      {/* central energy core */}
      <mesh ref={coreRef}>
        <circleGeometry args={[0.62, 48]} />
        <meshBasicMaterial color={CYAN} transparent opacity={0.75} />
      </mesh>
      <mesh rotation={[0, 0, Math.PI / 4]}>
        <ringGeometry args={[0.62, 0.66, 4]} />
        <meshBasicMaterial color={CYAN} transparent opacity={0.9} />
      </mesh>

      {/* inner circular geometry */}
      <group ref={innerRef}>
        <RingLine radius={1.05} thickness={0.015} opacity={0.7} />
        <RingNodes radius={1.05} count={6} />
      </group>

      {/* middle ring - concentric, counter-rotating */}
      <group ref={middleRef}>
        <RingLine radius={1.55} thickness={0.012} color={CYAN_DIM} opacity={0.6} />
        <TickMarks radius={1.55} count={72} />
      </group>

      {/* outer segmented ring */}
      <group ref={outerRef}>
        <SegmentedRing radius={2.05} count={40} arcFraction={0.5} thickness={0.03} />
      </group>

      {/* orbiting nodes ring */}
      <group ref={nodesRef}>
        <RingLine radius={2.35} thickness={0.006} color={CYAN_DIM} opacity={0.35} />
        <RingNodes radius={2.35} count={10} color={CYAN} />
      </group>

      {/* scanning sweep arc */}
      <group ref={scanRef}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.8, 0.008, 4, 64, Math.PI * 0.22]} />
          <meshBasicMaterial color={CYAN} transparent opacity={0.9} />
        </mesh>
      </group>
    </group>
  );
}
