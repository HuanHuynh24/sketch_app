import React from 'react';
import { UserRound, Target, MapPin, BookOpen, GraduationCap, Compass, Brain, Sparkles, RefreshCw, BarChart3, Zap } from 'lucide-react';
import Link from 'next/link';
import { DigitalCompetencyProfile, RiasecScore, RadarAxis, RiasecGroup } from '@/lib/api';

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const groupColors: Record<RiasecGroup, string> = {
  R: "#f43f5e", I: "#06b6d4", A: "#c084fc", S: "#10b981", E: "#f59e0b", C: "#94a3b8",
};

export function InfoPill({ icon: Icon, label, value, colorClass }: { icon: typeof UserRound; label: string; value: string; colorClass: string }) {
  return (
    <div className="glass-panel border border-white/5 p-5 rounded-2xl flex items-start gap-4 hover:border-white/20 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_10px_30px_rgba(0,0,0,0.3)] bg-black/20 group">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center border border-white/5 transition-transform duration-300 group-hover:scale-110 ${colorClass}`}>
        <Icon size={20} />
      </div>
      <div>
        <div className="text-xs font-bold text-[#94a3b8] uppercase tracking-wider mb-1">{label}</div>
        <div className="text-lg font-medium text-white truncate max-w-[200px]" title={value}>{value}</div>
      </div>
    </div>
  );
}



