"use client";

import { useState, useEffect } from "react";
import HomeStartButton from "@/app/HomeStartButton";
import { Brain, Target, Bot, Sparkles, ChevronRight } from "lucide-react";

export default function InteractiveHero() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    const handleMouseMove = (e: MouseEvent) => {
      // Normalize mouse coordinates from -1 to 1
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = (e.clientY / window.innerHeight) * 2 - 1;
      setMousePosition({ x, y });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  // Use 0 until mounted to prevent hydration mismatch
  const tiltX = isMounted ? mousePosition.y * -15 : 0; // max 15 deg
  const tiltY = isMounted ? mousePosition.x * 15 : 0;
  const parallaxX = isMounted ? mousePosition.x : 0;
  const parallaxY = isMounted ? mousePosition.y : 0;

  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 px-6 max-w-[1400px] mx-auto z-10 flex flex-col items-center text-center perspective-[2000px]">
      
      {/* Interactive Cursor Glow */}
      <div 
        className="absolute w-[800px] h-[800px] bg-gradient-to-tr from-[#06b6d4] to-[#8b5cf6] opacity-[0.15] blur-[120px] rounded-full pointer-events-none transition-transform duration-300 ease-out z-0"
        style={{
          transform: `translate(${parallaxX * 200}px, ${parallaxY * 200}px) scale(1.2)`,
        }}
      />

      {/* --- Text Content --- */}
      <div className="relative z-20 flex flex-col items-center transition-transform duration-700 ease-out"
           style={{ transform: `translate(${parallaxX * -10}px, ${parallaxY * -10}px)` }}>
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.15)] hover:bg-white/10 transition-colors cursor-pointer group">
          <Sparkles size={16} className="text-[#06b6d4] group-hover:animate-spin" />
          <span className="text-sm font-semibold tracking-wide text-[#cbd5e1]">Hệ Thống Tư Vấn Tuyển Sinh AI Thế Hệ Mới</span>
          <ChevronRight size={16} className="text-[#94a3b8] group-hover:translate-x-1 transition-transform" />
        </div>
        
        <h1 className="text-5xl md:text-7xl lg:text-[80px] font-black tracking-tighter leading-[1.1] mb-8 drop-shadow-2xl">
          Định Hướng Tương Lai <br />
          <span className="relative inline-block">
            <span className="absolute inset-0 blur-2xl opacity-50 bg-gradient-to-r from-[#06b6d4] via-[#8b5cf6] to-[#f43f5e]"></span>
            <span className="relative text-transparent bg-clip-text bg-gradient-to-r from-[#06b6d4] via-[#8b5cf6] to-[#f43f5e] animate-gradient">
              Bằng Trí Tuệ Nhân Tạo
            </span>
          </span>
        </h1>
        
        <p className="text-[#94a3b8] text-lg md:text-2xl max-w-3xl mb-12 leading-relaxed font-medium">
          Dừng việc chọn ngành theo cảm tính. Trải nghiệm hệ thống AI phân tích năng lực RIASEC đa chiều và dự báo điểm chuẩn với độ chính xác lên đến 98%.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center gap-6 relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-[#06b6d4] to-[#f43f5e] blur-xl opacity-20 group-hover:opacity-60 transition-opacity duration-500 rounded-full" />
          <HomeStartButton
            id="hero-cta-start"
            className="relative w-full sm:w-auto px-10 py-5 text-xl font-bold bg-white text-black border-2 border-transparent hover:border-white transition-all rounded-full shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:scale-105 hover:bg-transparent hover:text-white"
          />
        </div>
      </div>

      {/* --- 3D Floating UI Preview --- */}
      <div className="mt-24 w-full relative h-[400px] md:h-[600px] flex justify-center items-center transform-style-3d">
        
        {/* Main Center Card (3D Tilt) */}
        <div 
          className="absolute z-30 w-[90%] md:w-[700px] h-[350px] md:h-[450px] glass-panel bg-black/60 backdrop-blur-3xl border border-white/20 rounded-[2.5rem] shadow-[0_30px_100px_rgba(6,182,212,0.3)] flex flex-col p-8 transition-transform duration-200 ease-out overflow-hidden"
          style={{
            transform: `rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateZ(50px) scale(1.05)`,
            transformStyle: "preserve-3d"
          }}
        >
          {/* Moving scanline inside card */}
          <div 
            className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-[#06b6d4] to-transparent opacity-80"
            style={{ 
              transform: `translateY(${((parallaxY + 1) / 2) * 450}px)`,
              transition: 'transform 0.1s linear'
            }}
          />

          <div className="flex justify-between items-center mb-8 relative" style={{ transform: "translateZ(30px)" }}>
             <div className="flex items-center gap-3">
               <div className="p-3 bg-[#8b5cf6]/20 rounded-2xl border border-[#8b5cf6]/30 shadow-[0_0_20px_rgba(139,92,246,0.3)]">
                  <Brain size={28} className="text-[#8b5cf6]" />
               </div>
               <div className="text-left">
                 <h3 className="font-bold text-white text-xl drop-shadow-md">Phân tích RIASEC</h3>
                 <span className="text-sm text-[#06b6d4] font-medium tracking-wide">AI Đang xử lý trực tiếp...</span>
               </div>
             </div>
             <span className="px-4 py-2 bg-emerald-500/10 text-emerald-400 font-bold rounded-full border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.3)] animate-pulse">98% Độ Tương Thích</span>
          </div>
          
          <div className="space-y-6 flex-1 flex flex-col justify-center relative" style={{ transform: "translateZ(40px)" }}>
             {[
               { label: "Realistic (Kỹ thuật)", val: 72, color: "from-[#06b6d4] to-[#3b82f6]", shadow: "shadow-[#06b6d4]" },
               { label: "Investigative (Nghiên cứu)", val: 85, color: "from-[#8b5cf6] to-[#d946ef]", shadow: "shadow-[#8b5cf6]" },
               { label: "Artistic (Nghệ thuật)", val: 40, color: "from-[#f43f5e] to-[#fb923c]", shadow: "shadow-[#f43f5e]" }
             ].map((item, idx) => (
               <div key={idx} className="group cursor-default">
                 <div className="flex justify-between text-sm font-bold text-[#94a3b8] mb-2 uppercase tracking-widest group-hover:text-white transition-colors">
                   <span>{item.label}</span>
                   <span className="text-white drop-shadow-md">{item.val} / 100</span>
                 </div>
                 <div className="h-4 bg-black/40 rounded-full overflow-hidden border border-white/5 relative">
                   <div 
                     className={`absolute top-0 left-0 h-full w-[${item.val}%] bg-gradient-to-r ${item.color} rounded-full shadow-[0_0_15px_${item.shadow.split('-')[1]}]`}
                     style={{ width: `${item.val}%` }}
                   />
                 </div>
               </div>
             ))}
          </div>
        </div>

        {/* Left Floating Card (Parallax) */}
        <div 
          className="absolute z-20 left-[0%] md:left-[5%] top-[15%] w-[250px] md:w-[340px] p-6 glass-panel bg-black/70 backdrop-blur-md border border-white/10 rounded-3xl shadow-2xl hidden sm:block transition-transform duration-300 ease-out"
          style={{
            transform: `translateX(${parallaxX * -40}px) translateY(${parallaxY * -60}px) rotate(-8deg) translateZ(-50px)`
          }}
        >
           <div className="flex items-center gap-4 mb-4">
             <div className="p-2 bg-[#06b6d4]/20 rounded-xl">
               <Bot size={24} className="text-[#06b6d4]" />
             </div>
             <span className="font-bold text-white text-lg">Cố vấn tức thì</span>
           </div>
           <p className="text-sm text-[#94a3b8] leading-relaxed">"Với điểm 26.1, ngành CNTT Bách Khoa có rủi ro cao. Bạn nên đặt NV1 là ĐH Công nghệ..."</p>
        </div>

        {/* Right Floating Card (Parallax) */}
        <div 
          className="absolute z-40 right-[0%] md:right-[5%] bottom-[15%] w-[250px] md:w-[300px] p-6 glass-panel bg-black/70 backdrop-blur-md border border-white/10 rounded-3xl shadow-2xl hidden sm:block transition-transform duration-300 ease-out"
          style={{
            transform: `translateX(${parallaxX * 60}px) translateY(${parallaxY * 60}px) rotate(8deg) translateZ(80px)`
          }}
        >
           <div className="flex items-center gap-4 mb-4">
             <div className="p-2 bg-[#f43f5e]/20 rounded-xl">
               <Target size={24} className="text-[#f43f5e]" />
             </div>
             <span className="font-bold text-white text-lg">Dự báo chuẩn</span>
           </div>
           <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-[#94a3b8] mb-1">28.5 <span className="text-sm font-bold text-[#94a3b8] tracking-widest uppercase">Điểm</span></div>
           <div className="text-sm text-emerald-400 font-bold bg-emerald-400/10 inline-block px-2 py-1 rounded-md">+0.3 so với 2024</div>
        </div>

      </div>
    </section>
  );
}
