import React from 'react';
import { UniversityOption } from './data';
import { GraduationCap, Briefcase, Zap, MapPin } from 'lucide-react';

export function UniversityCard({ option, selected, onClick }: { option: UniversityOption, selected: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left glass-panel p-5 rounded-3xl transition-all duration-300 border relative overflow-hidden group
        ${selected ? "bg-[#06b6d4]/10 border-[#06b6d4]/50 shadow-[0_0_30px_rgba(6,182,212,0.2)] scale-[1.02]" : "bg-black/40 border-white/10 hover:border-white/30 hover:bg-black/60"}
      `}
    >
      {selected && <div className="absolute inset-0 bg-gradient-to-r from-[#06b6d4]/10 to-transparent"></div>}
      <div className="flex justify-between items-start relative z-10">
        <div>
          <h4 className="text-xl font-bold text-white mb-1 group-hover:text-[#06b6d4] transition-colors">{option.shortName}</h4>
          <p className="text-sm text-[#94a3b8]">{option.major}</p>
        </div>
        <div className="text-right">
           <div className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#06b6d4] to-[#c084fc]">
             {option.matchPercent}%
           </div>
           <div className="text-[10px] uppercase font-bold text-[#94a3b8] tracking-widest">Độ phù hợp</div>
        </div>
      </div>
      <div className="flex items-center gap-3 mt-4 relative z-10">
        <span className="px-2 py-1 bg-white/5 border border-white/10 rounded-md text-xs text-white/70 flex items-center gap-1">
          <Zap size={12} className="text-[#f59e0b]" /> {option.predicted} điểm
        </span>
        <span className="px-2 py-1 bg-white/5 border border-white/10 rounded-md text-xs text-white/70 flex items-center gap-1">
          <MapPin size={12} className="text-[#10b981]" /> {option.location}
        </span>
      </div>
    </button>
  );
}
