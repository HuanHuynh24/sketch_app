import React from 'react';
import { UniversityOption } from './data';
import { Target, BookOpen, Briefcase, ChevronRight, GraduationCap } from 'lucide-react';

export function DetailPanel({ option }: { option: UniversityOption }) {
  return (
    <div className="glass-panel bg-black/40 border border-white/10 p-8 rounded-3xl overflow-auto custom-scrollbar h-full flex flex-col gap-8">
       <div className="flex items-center gap-5">
         <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#06b6d4]/20 to-[#c084fc]/20 border border-[#06b6d4]/30 flex items-center justify-center">
           <GraduationCap size={32} className="text-[#06b6d4]" />
         </div>
         <div>
           <h2 className="text-3xl font-black text-white tracking-tight">{option.university}</h2>
           <p className="text-[#06b6d4] font-medium text-lg">{option.major} · {option.shortName}</p>
         </div>
       </div>
       
       <div className="grid grid-cols-2 gap-4">
         <div className="bg-white/5 p-4 rounded-2xl border border-white/10">
           <div className="text-sm font-bold text-[#94a3b8] uppercase mb-1">Xác suất đỗ</div>
           <div className="text-2xl font-black text-emerald-400">{option.matchPercent}%</div>
         </div>
         <div className="bg-white/5 p-4 rounded-2xl border border-white/10">
           <div className="text-sm font-bold text-[#94a3b8] uppercase mb-1">Học phí / Năm</div>
           <div className="text-2xl font-black text-white">~35tr</div>
         </div>
       </div>

       <div className="space-y-4">
         <h3 className="text-xl font-bold text-white flex items-center gap-2"><Target className="text-[#f43f5e]"/> Tại sao phù hợp?</h3>
         <p className="text-[#94a3b8] leading-relaxed">Chương trình đào tạo thiên về thực hành (R) và nghiên cứu (I), khớp 90% với hồ sơ năng lực của bạn. Cơ hội thực tập ngay từ năm 3 tại các tập đoàn lớn.</p>
       </div>
    </div>
  );
}
