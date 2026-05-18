import React from 'react';
import Link from 'next/link';
import { BarChart3, Brain, Compass, Zap, Bot, LoaderCircle, Sparkles, AlertTriangle } from 'lucide-react';
import { DigitalCompetencyProfile, RiasecScore, RadarAxis, RiasecGroup } from '@/lib/api';

type SubmitStage = "idle" | "sending" | "waiting";

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const groupColors: Record<RiasecGroup, string> = {
  R: "#f43f5e", I: "#06b6d4", A: "#c084fc", S: "#10b981", E: "#f59e0b", C: "#94a3b8",
};


import { ScoreBars } from './ScoreBars';
import { RiasecRadar } from './RiasecRadar';

export function ResultPanel({ profile }: { profile: DigitalCompetencyProfile }) {
  const axes = profile.radar_chart?.axes ?? [];
  const dominantGroups = profile.dominant_groups ?? [];
  const groupAnalysis = profile.group_analysis ?? [];
  const recommendations = profile.career_recommendations;

  return (
    <div className="w-full max-w-5xl mx-auto my-8 animate-[slideUp_0.8s_ease-out_forwards] opacity-0" style={{ animationFillMode: 'forwards' }}>
      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .hud-border {
          background: linear-gradient(90deg, rgba(6,182,212,0.5) 0%, transparent 20%, transparent 80%, rgba(124,58,237,0.5) 100%);
          height: 1px;
          width: 100%;
        }
      `}</style>
      
      {/* Massive Glowing Title Card */}
      <div className="glass-panel border-t border-white/20 rounded-[2.5rem] p-8 md:p-12 bg-black/40 backdrop-blur-2xl relative overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
        
        {/* Dynamic Background */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-[#7c3aed] opacity-30 blur-[120px] rounded-full animate-pulse-glow pointer-events-none"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-[#06b6d4] opacity-20 blur-[120px] rounded-full animate-float-smooth pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col items-center text-center mb-16">
          <div className="inline-flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-white/10 to-white/5 border border-white/10 rounded-full text-sm font-bold text-[#06b6d4] uppercase tracking-[0.2em] mb-6 shadow-[0_0_20px_rgba(6,182,212,0.3)]">
            <Sparkles size={16} className="text-[#c084fc]" /> Hồ sơ năng lực phân tích bởi AI
          </div>
          <h3 className="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white via-white to-[#7c3aed] mb-6 filter drop-shadow-lg">
            {profile.riasec_code}
          </h3>
          <p className="max-w-3xl text-[#94a3b8] text-lg md:text-xl leading-relaxed">
            {profile.summary}
          </p>
          <div className="mt-8">
            <Link
              href={`/profile?dcp_id=${profile.dcp_id}`}
              className="btn-premium inline-flex items-center justify-center gap-3 px-8 py-4 text-lg"
            >
              <Compass size={20} /> Khám phá chi tiết hành trình
            </Link>
          </div>
        </div>

        <div className="hud-border mb-12"></div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_450px] gap-8 relative z-10">
          
          {/* Radar Column */}
          <div className="flex flex-col">
            <div className="flex items-center gap-3 mb-8">
               <div className="w-10 h-10 rounded-xl bg-[#06b6d4]/20 flex items-center justify-center border border-[#06b6d4]/30 shadow-[0_0_15px_rgba(6,182,212,0.4)]">
                 <BarChart3 size={20} className="text-[#06b6d4]" />
               </div>
               <h4 className="text-2xl font-bold text-white tracking-tight">Biểu đồ Phân cực Năng lực</h4>
            </div>
            
            <div className="bg-black/30 rounded-3xl p-6 border border-white/5 flex-1 flex flex-col justify-center">
              <RiasecRadar axes={axes} />
              <ScoreBars scores={profile.scores} />
            </div>
          </div>

          {/* Details Column */}
          <div className="flex flex-col gap-6">
            
            {/* Dominant Traits */}
            <div className="bg-black/30 rounded-3xl p-6 border border-white/5 relative overflow-hidden">
               <div className="absolute top-0 right-0 w-32 h-32 bg-[#c084fc] opacity-10 blur-3xl"></div>
               <h4 className="text-white mb-6 flex items-center gap-3 text-xl font-bold">
                <Brain size={20} className="text-[#c084fc]" /> Đặc điểm nổi bật
              </h4>
              <div className="space-y-4">
                {dominantGroups.map((group) => (
                  <div key={group.group} className="flex gap-4 items-start group">
                    <div className="shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold border" style={{ backgroundColor: `${groupColors[group.group]}15`, borderColor: `${groupColors[group.group]}40`, color: groupColors[group.group] }}>
                      {group.group}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-lg text-white group-hover:text-white transition-colors">{group.label}</span>
                        <span className="px-2 py-0.5 bg-white/10 rounded text-[10px] font-mono text-white/70">{group.score.toFixed(1)}</span>
                      </div>
                      <p className="text-sm text-[#94a3b8] leading-relaxed line-clamp-2 group-hover:line-clamp-none transition-all">{group.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Career Matches */}
            <div className="bg-black/30 rounded-3xl p-6 border border-white/5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#f59e0b] opacity-10 blur-3xl"></div>
              <h4 className="text-white mb-6 flex items-center gap-3 text-xl font-bold">
                <Zap size={20} className="text-[#f59e0b]" /> Gợi ý Ngành nghề
              </h4>
              <div className="flex flex-wrap gap-2 mb-6">
                {(recommendations?.recommended_majors ?? profile.recommended_majors).slice(0, 6).map((major) => (
                  <span key={major} className="px-4 py-2 bg-[#f59e0b]/10 border border-[#f59e0b]/30 text-[#f59e0b] rounded-xl text-sm font-bold shadow-[0_0_10px_rgba(245,158,11,0.1)]">
                    {major}
                  </span>
                ))}
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <p className="text-xs text-[#94a3b8] uppercase tracking-wider mb-2 font-bold">Vai trò công việc phù hợp</p>
                <p className="text-sm text-white/90 leading-relaxed">
                  {(recommendations?.suitable_roles ?? []).slice(0, 5).join(", ") || "Đang cập nhật..."}
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}



