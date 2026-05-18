import React from 'react';
import Link from 'next/link';
import { BarChart3, Brain, Compass, Zap, Bot, LoaderCircle, Sparkles, AlertTriangle } from 'lucide-react';
import { DigitalCompetencyProfile, RiasecScore, RadarAxis, RiasecGroup } from '@/lib/api';

type SubmitStage = "idle" | "sending" | "waiting";

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const groupColors: Record<RiasecGroup, string> = {
  R: "#f43f5e", I: "#06b6d4", A: "#c084fc", S: "#10b981", E: "#f59e0b", C: "#94a3b8",
};

export function SubmitStatus({ stage }: { stage: SubmitStage }) {
  if (stage === "idle") return null;

  const isSending = stage === "sending";

  return (
    <div
      role="status"
      aria-live="polite"
      className="self-start flex flex-col gap-2 max-w-[85%] md:max-w-[70%] animate-[slideUp_0.3s_ease-out_forwards]"
    >
      <div className="flex items-center gap-4 ml-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#7c3aed] to-[#06b6d4] flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.6)] animate-pulse relative">
           <div className="absolute inset-0 rounded-xl bg-white opacity-20 animate-ping"></div>
           <Bot size={20} className="text-white relative z-10" />
        </div>
        <div className="glass-panel px-5 py-4 rounded-[1.5rem] rounded-tl-sm border-white/10 relative overflow-hidden shadow-xl bg-black/40">
           {/* Shimmer effect */}
           <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent animate-[shimmer_1.5s_infinite]"></div>
           <div className="flex items-center gap-3 text-sm font-bold text-[#06b6d4] tracking-wide">
             <LoaderCircle size={16} className="animate-spin" />
             {isSending ? "HỆ THỐNG ĐANG TIẾP NHẬN..." : "AI ĐANG PHÂN TÍCH TÂM LÝ..."}
           </div>
        </div>
      </div>
    </div>
  );
}

