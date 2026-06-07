"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import type { Group, Mesh } from "three";

type StagePointer = {
  x: number;
  y: number;
  active: boolean;
};

const skillColors = ["#0d9488", "#3867d6", "#f9735b", "#7c4dff", "#d99a28", "#0f766e", "#ef5da8", "#4f46e5"];

function NeuralGraph({ pointerRef }: { pointerRef: React.RefObject<StagePointer> }) {
  const group = useRef<Group>(null);
  const nodeRefs = useRef<Array<Mesh | null>>([]);
  const nodes = useMemo(
    () =>
      Array.from({ length: 44 }, (_, index) => ({
        index,
        x: Math.sin(index * 1.7) * (1.4 + (index % 5) * 0.18),
        y: Math.cos(index * 0.9) * (0.9 + (index % 4) * 0.16),
        z: Math.sin(index * 0.6) * 1.3,
        lift: 0.2 + (index % 6) * 0.08,
        color: skillColors[index % skillColors.length]
      })),
    []
  );

  useFrame(({ clock }) => {
    if (!group.current || !pointerRef.current) return;
    const pointer = pointerRef.current;
    const cursorForce = pointer.active ? 1 : 0.24;
    group.current.rotation.y = clock.elapsedTime * 0.09 + pointer.x * 0.34 * cursorForce;
    group.current.rotation.x = Math.sin(clock.elapsedTime * 0.25) * 0.08 - pointer.y * 0.18 * cursorForce;
    group.current.position.x = pointer.x * 0.16 * cursorForce;
    group.current.position.y = pointer.y * 0.12 * cursorForce;

    nodeRefs.current.forEach((mesh, index) => {
      if (!mesh) return;
      const node = nodes[index];
      const wave = Math.sin(clock.elapsedTime * (0.8 + index * 0.015) + index) * node.lift;
      const distanceFromCursor = Math.max(0, 1 - Math.hypot(pointer.x - node.x / 3, pointer.y - node.y / 2.2));
      const magnet = pointer.active ? distanceFromCursor * 0.55 : 0;
      mesh.position.x = node.x + pointer.x * magnet;
      mesh.position.y = node.y + wave + pointer.y * magnet;
      mesh.position.z = node.z + magnet * 0.8;
      const scale = 1 + magnet * 1.8 + Math.sin(clock.elapsedTime * 1.4 + index) * 0.04;
      mesh.scale.setScalar(scale);
    });
  });

  return (
    <group ref={group}>
      {nodes.map((node, index) => (
        <mesh
          key={node.index}
          position={[node.x, node.y, node.z]}
          ref={(mesh) => {
            nodeRefs.current[index] = mesh;
          }}
        >
          <sphereGeometry args={[node.index % 7 === 0 ? 0.08 : 0.048, 24, 24]} />
          <meshStandardMaterial color={node.color} emissive={node.color} emissiveIntensity={0.5} />
        </mesh>
      ))}
      {nodes.slice(0, 30).map((node) => {
        const height = Math.abs(node.y) + 1.75 + (node.index % 5) * 0.28;
        return (
          <mesh key={`signal-${node.index}`} position={[node.x, -1.68 + height / 2, node.z - 0.18]}>
            <cylinderGeometry args={[0.005, 0.005, height, 6]} />
            <meshStandardMaterial color="#00ffcc" transparent opacity={0.08} />
          </mesh>
        );
      })}
      {nodes.slice(0, 22).map((node, index) => {
        const next = nodes[(index * 3 + 5) % nodes.length];
        const mid = [(node.x + next.x) / 2, (node.y + next.y) / 2, (node.z + next.z) / 2] as [number, number, number];
        const distance = Math.hypot(node.x - next.x, node.y - next.y, node.z - next.z);
        const angle = Math.atan2(next.y - node.y, next.x - node.x);
        return (
          <mesh
            key={`${node.index}-${next.index}`}
            position={mid}
            rotation={[0, 0, angle]}
          >
            <cylinderGeometry args={[0.006, 0.006, distance, 8]} />
            <meshStandardMaterial color="#00ffcc" transparent opacity={0.12} />
          </mesh>
        );
      })}
    </group>
  );
}

export default function TwinGraph({ pointerRef }: { pointerRef: React.RefObject<StagePointer> }) {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 54 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[4, 5, 5]} intensity={60} color="#00ffcc" />
      <pointLight position={[-3, -2, 2]} intensity={25} color="#ff4d6a" />
      <pointLight position={[0, -3, 3]} intensity={15} color="#4d8cff" />
      <NeuralGraph pointerRef={pointerRef} />
    </Canvas>
  );
}
