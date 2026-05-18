import React from 'react';

export function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

export function MiniRadar({ size = 120 }: { size?: number }) {
  const cx = size / 2;
  const cy = size / 2;
  const maxR = size * 0.4;
  const groups = ["R", "I", "A", "S", "E", "C"];
  const colors = ["#f43f5e", "#06b6d4", "#c084fc", "#10b981", "#f59e0b", "#94a3b8"];
  // Mock data for display
  const scores = [80, 95, 60, 40, 70, 55];

  const dataPoints = scores.map((val, i) => polarToCart(cx, cy, (val / 100) * maxR, i * 60));
  const pathD = dataPoints.map((pt, i) => `${i === 0 ? "M" : "L"} ${pt.x} ${pt.y}`).join(" ") + " Z";

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <div className="absolute inset-0 bg-[#06b6d4] opacity-20 blur-xl rounded-full"></div>
      <svg viewBox={`0 0 ${size} ${size}`} className="w-full h-full relative z-10">
        <circle cx={cx} cy={cy} r={maxR} fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.1)" />
        <circle cx={cx} cy={cy} r={maxR * 0.5} fill="none" stroke="rgba(255,255,255,0.05)" />
        {groups.map((g, i) => {
          const end = polarToCart(cx, cy, maxR, i * 60);
          const label = polarToCart(cx, cy, maxR + 10, i * 60);
          return (
            <g key={g}>
              <line x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="rgba(255,255,255,0.1)" />
              <text x={label.x} y={label.y} textAnchor="middle" dominantBaseline="middle" fill={colors[i]} fontSize="10" fontWeight="bold">
                {g}
              </text>
            </g>
          );
        })}
        <path d={pathD} fill="rgba(6,182,212,0.3)" stroke="#06b6d4" strokeWidth="1.5" />
      </svg>
    </div>
  );
}
