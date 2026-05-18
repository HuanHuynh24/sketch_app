import React from 'react';
import { Target, Compass } from 'lucide-react';

export function BridgeScreen({ onStart }: { onStart: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#030014] text-white">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-20 [mask-image:linear-gradient(180deg,white,transparent)]"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[radial-gradient(circle,rgba(6,182,212,0.15)_0%,transparent_60%)] animate-pulse-slow"></div>
      
      <div className="glass-panel bg-black/40 backdrop-blur-3xl border border-white/10 rounded-[3rem] p-16 max-w-3xl text-center relative z-10 shadow-[0_20px_80px_rgba(6,182,212,0.2)]">
         <div className="w-24 h-24 bg-gradient-to-br from-[#06b6d4] to-[#8b5cf6] rounded-3xl mx-auto flex items-center justify-center mb-8 shadow-[0_0_30px_rgba(6,182,212,0.4)]">
           <Compass size={40} className="text-white" />
         </div>
         <h1 className="text-5xl md:text-6xl font-black mb-6 tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white to-[#94a3b8]">
           Không Gian Tư Vấn Tuyển Sinh
         </h1>
         <p className="text-xl text-[#94a3b8] mb-12 max-w-xl mx-auto leading-relaxed">
           Hệ thống đã chuẩn bị sẵn các lựa chọn trường đại học tối ưu nhất dựa trên phân tích RIASEC và điểm số của bạn.
         </p>
         <button onClick={onStart} className="btn-premium px-10 py-5 text-xl w-full max-w-md shadow-[0_0_30px_rgba(124,58,237,0.5)]">
           Tiến vào Bảng Điều Khiển
         </button>
      </div>
    </div>
  );
}
