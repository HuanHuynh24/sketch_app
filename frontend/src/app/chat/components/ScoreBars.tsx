import React from 'react';
import Link from 'next/link';
import { BarChart3, Brain, Compass, Zap, Bot, LoaderCircle, Sparkles, AlertTriangle } from 'lucide-react';
import { DigitalCompetencyProfile, RiasecScore, RadarAxis, RiasecGroup } from '@/lib/api';

type SubmitStage = "idle" | "sending" | "waiting";

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const groupColors: Record<RiasecGroup, string> = {
  R: "#f43f5e", I: "#06b6d4", A: "#c084fc", S: "#10b981", E: "#f59e0b", C: "#94a3b8",
};

export function ScoreBars({ scores }: { scores: RiasecScore }) {
  const maxScore = Math.max(1, ...riasecGroups.map((group) => scores[group] ?? 0));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
      {riasecGroups.map((group) => {
        const value = scores[group] ?? 0;
        const width = `${Math.max(5, (value / maxScore) * 100)}%`;

        return (
          <div key={group} className="flex flex-col gap-2 bg-white/5 p-3 rounded-2xl border border-white/5 relative overflow-hidden group hover:border-white/20 transition-all">
            <div className="absolute top-0 right-0 w-16 h-16 opacity-10 blur-xl transition-all group-hover:opacity-30" style={{ backgroundColor: groupColors[group] }}></div>
            <div className="flex items-center justify-between z-10">
              <span
                className="w-8 h-8 flex items-center justify-center rounded-xl bg-black/40 border border-white/10 font-bold shadow-lg text-sm"
                style={{ fontFamily: "var(--font-heading)", color: groupColors[group] }}
              >
                {group}
              </span>
              <span className="text-xl font-bold text-white/90 font-mono tracking-tight">{value.toFixed(1)}</span>
            </div>
            <div className="w-full h-1.5 bg-black/50 rounded-full overflow-hidden shadow-inner z-10">
              <div className="h-full rounded-full transition-all duration-1000 ease-out" style={{ width, backgroundColor: groupColors[group], boxShadow: `0 0 10px ${groupColors[group]}` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}



