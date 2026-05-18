import React from 'react';
import { Target, Zap, Brain, ChevronRight } from 'lucide-react';
import { MiniRadar } from './MiniRadar';

export function ProfileHeader() {
  return (
    <div className="w-full glass-panel bg-black/40 backdrop-blur-2xl border border-white/10 rounded-[2rem] p-6 mb-8 flex flex-col md:flex-row items-center gap-8 shadow-[0_20px_50px_rgba(0,0,0,0.3)]">
      <div className="flex items-center gap-6 flex-1">
        <MiniRadar size={100} />
        <div>
          <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-[#94a3b8] mb-2">Nguyễn Văn An</h2>
          <div className="flex items-center gap-3">
             <span className="px-3 py-1 bg-[#06b6d4]/10 text-[#06b6d4] text-sm font-bold border border-[#06b6d4]/30 rounded-full">A00: 26.1</span>
             <span className="px-3 py-1 bg-[#8b5cf6]/10 text-[#8b5cf6] text-sm font-bold border border-[#8b5cf6]/30 rounded-full">HB: 8.4</span>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
         <div className="text-right">
           <div className="text-sm font-bold text-[#94a3b8] mb-1">Thiên hướng RIASEC</div>
           <div className="flex items-center gap-2 justify-end">
             <span className="w-8 h-8 rounded-full bg-[#06b6d4]/20 border border-[#06b6d4]/40 flex items-center justify-center text-[#06b6d4] font-bold text-sm">I</span>
             <span className="w-8 h-8 rounded-full bg-[#10b981]/20 border border-[#10b981]/40 flex items-center justify-center text-[#10b981] font-bold text-sm">S</span>
           </div>
         </div>
      </div>
    </div>
  );
}
