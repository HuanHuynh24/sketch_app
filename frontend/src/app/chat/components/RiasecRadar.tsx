import React from 'react';
import Link from 'next/link';
import { BarChart3, Brain, Compass, Zap, Bot, LoaderCircle, Sparkles, AlertTriangle } from 'lucide-react';
import { DigitalCompetencyProfile, RiasecScore, RadarAxis, RiasecGroup } from '@/lib/api';

type SubmitStage = "idle" | "sending" | "waiting";

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const groupColors: Record<RiasecGroup, string> = {
  R: "#f43f5e", I: "#06b6d4", A: "#c084fc", S: "#10b981", E: "#f59e0b", C: "#94a3b8",
};

export function RiasecRadar({ axes }: { axes: RadarAxis[] }) {
  const cx = 180;
  const cy = 180;
  const maxR = 120;
  const levels = [0.25, 0.5, 0.75, 1];
  const normalizedAxes = riasecGroups.map((group, index) => {
    const axis = axes.find((item) => item.group === group);
    return {
      group,
      label: axis?.label ?? group,
      value: axis?.normalized_score ?? 0,
      rawScore: axis?.score ?? 0,
      confidence: axis?.confidence ?? 0,
      angle: index * 60,
    };
  });
  const dataPoints = normalizedAxes.map((axis) =>
    polarToCart(cx, cy, (axis.value / 100) * maxR, axis.angle),
  );
  const pathD = `${dataPoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ")} Z`;

  return (
    <div className="relative w-full max-w-[400px] aspect-square mx-auto flex items-center justify-center">
      {/* Intense glow behind radar */}
      <div className="absolute inset-0 bg-[#06b6d4] opacity-10 blur-[80px] rounded-full"></div>
      
      <svg viewBox="0 0 360 360" className="w-full h-full relative z-10 drop-shadow-2xl" role="img" aria-label="Biểu đồ radar RIASEC">
        <defs>
          <radialGradient id="radarGridGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.02)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </radialGradient>
          <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
             <feGaussianBlur stdDeviation="4" result="blur" />
             <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
             </feMerge>
          </filter>
        </defs>

        <circle cx={cx} cy={cy} r={maxR} fill="url(#radarGridGlow)" />

        {levels.map((level) => {
          const pts = normalizedAxes
            .map((axis) => polarToCart(cx, cy, maxR * level, axis.angle))
            .map((point) => `${point.x},${point.y}`)
            .join(" ");

          return <polygon key={level} points={pts} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="1" strokeDasharray={level === 1 ? "none" : "4 4"} />;
        })}

        {normalizedAxes.map((axis) => {
          const end = polarToCart(cx, cy, maxR, axis.angle);
          const label = polarToCart(cx, cy, maxR + 32, axis.angle);

          return (
            <g key={axis.group}>
              <line x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
              <text
                x={label.x}
                y={label.y}
                textAnchor="middle"
                dominantBaseline="middle"
                style={{ fontFamily: "var(--font-heading)", fontSize: 18, fontWeight: 800, fill: groupColors[axis.group], filter: "drop-shadow(0px 2px 4px rgba(0,0,0,0.5))" }}
              >
                {axis.group}
              </text>
            </g>
          );
        })}

        <path 
          d={pathD} 
          fill="rgba(6, 182, 212, 0.25)" 
          stroke="#06b6d4" 
          strokeWidth="3" 
          filter="url(#neonGlow)"
          className="animate-[pulse_3s_ease-in-out_infinite]"
        />
        
        {dataPoints.map((point, index) => {
          const axis = normalizedAxes[index];
          return (
            <g key={axis.group}>
              <circle 
                cx={point.x} 
                cy={point.y} 
                r="6" 
                fill={groupColors[axis.group]} 
                stroke="#ffffff" 
                strokeWidth="2" 
                style={{ filter: `drop-shadow(0 0 6px ${groupColors[axis.group]})` }} 
              />
              <circle cx={point.x} cy={point.y} r="12" fill={groupColors[axis.group]} opacity="0.2" className="animate-ping" />
            </g>
          );
        })}
      </svg>
    </div>
  );
}


export function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

