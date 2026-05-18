import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HomeStartButton from "./HomeStartButton";
import Link from "next/link";
import {
  Brain, BarChart3, Target, GraduationCap, TrendingUp,
  Bot, Database, ShieldCheck, Zap, LineChart,
  Compass, Sparkles, ChevronRight, Activity, Globe, Stars
} from "lucide-react";
import InteractiveHero from "@/components/InteractiveHero";

export default function Home() {
  return (
    <div className="relative overflow-hidden bg-[#030014] text-white selection:bg-[#06b6d4] selection:text-white">
      {/* Background Deep Space Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[1000px] h-[1000px] rounded-full bg-[radial-gradient(circle,rgba(124,58,237,0.15)_0%,transparent_60%)] animate-pulse-slow pointer-events-none" />
      <div className="absolute top-[20%] right-[-20%] w-[1200px] h-[1200px] rounded-full bg-[radial-gradient(circle,rgba(6,182,212,0.1)_0%,transparent_60%)] pointer-events-none" />
      
      {/* Subtle Grid Pattern */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-20 pointer-events-none" />

      <Navbar />

      {/* --- HERO SECTION --- */}
      <InteractiveHero />

      {/* --- MARQUEE --- */}
      <div className="w-full border-y border-white/10 bg-black/50 backdrop-blur-md py-10 overflow-hidden my-12 relative z-20 flex flex-col gap-6">
        {/* Forward Marquee */}
        <div className="animate-marquee whitespace-nowrap font-black text-4xl md:text-5xl tracking-[0.2em] uppercase flex items-center">
          {[1, 2].map((i) => (
            <div key={`fw-${i}`} className="flex">
              <span className="mx-12 flex items-center gap-6 text-white drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]"><Stars size={40} className="text-[#06b6d4]"/> AI ASSESSMENT</span>
              <span className="mx-12 flex items-center gap-6 text-stroke-glass hover:text-white"><Database size={40} className="text-[#8b5cf6]"/> BIG DATA ANALYTICS</span>
              <span className="mx-12 flex items-center gap-6 text-white drop-shadow-[0_0_15px_rgba(244,63,94,0.5)]"><Target size={40} className="text-[#f43f5e]"/> PREDICTIVE MODEL</span>
              <span className="mx-12 flex items-center gap-6 text-stroke-glass hover:text-white"><ShieldCheck size={40} className="text-emerald-400"/> 98% ACCURACY</span>
            </div>
          ))}
        </div>
        {/* Reverse Marquee */}
        <div className="animate-marquee-reverse whitespace-nowrap font-black text-4xl md:text-5xl tracking-[0.2em] uppercase flex items-center opacity-70">
          {[1, 2].map((i) => (
            <div key={`rev-${i}`} className="flex">
              <span className="mx-12 flex items-center gap-6 text-stroke-glass hover:text-white"><Brain size={40} className="text-[#06b6d4]"/> DEEP LEARNING</span>
              <span className="mx-12 flex items-center gap-6 text-white drop-shadow-[0_0_15px_rgba(139,92,246,0.5)]"><TrendingUp size={40} className="text-[#8b5cf6]"/> REALTIME INSIGHTS</span>
              <span className="mx-12 flex items-center gap-6 text-stroke-glass hover:text-white"><GraduationCap size={40} className="text-[#f43f5e]"/> ADMISSION 2025</span>
              <span className="mx-12 flex items-center gap-6 text-white drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]"><Zap size={40} className="text-emerald-400"/> SMART CHOICES</span>
            </div>
          ))}
        </div>
      </div>

      {/* --- BENTO GRID (Features) --- */}
      <section id="features" className="py-32 px-6 max-w-[1400px] mx-auto relative z-10">
        <div className="text-center mb-24">
          <h2 className="text-5xl md:text-6xl font-black tracking-tight mb-6">Trải Nghiệm <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#06b6d4] to-[#8b5cf6]">Đẳng Cấp</span></h2>
          <p className="text-[#94a3b8] text-xl max-w-2xl mx-auto font-medium">Bỏ qua những công cụ tư vấn lỗi thời. Chúng tôi mang đến hệ sinh thái công nghệ giúp bạn tự tin quyết định.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[320px]">
          {/* Card 1: Large Wide */}
          <div className="md:col-span-2 glass-panel bg-black/40 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-10 relative overflow-hidden group hover:border-[#06b6d4]/50 transition-colors duration-500">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#06b6d4]/10 blur-3xl rounded-full transition-all group-hover:bg-[#06b6d4]/20" />
            <Brain size={40} className="text-[#06b6d4] mb-6" />
            <h3 className="text-3xl font-bold text-white mb-4">Hồ Sơ Năng Lực AI</h3>
            <p className="text-lg text-[#94a3b8] max-w-md leading-relaxed">Đánh giá chuyên sâu qua bài test tương tác. Khám phá thiên hướng bẩm sinh dựa trên lý thuyết Holland RIASEC được AI cá nhân hóa.</p>
            <div className="absolute bottom-[-20%] right-[-5%] opacity-50 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none">
              <svg width="300" height="300" viewBox="0 0 100 100" className="text-[#06b6d4]/20 fill-current">
                <polygon points="50,5 90,25 90,75 50,95 10,75 10,25" />
              </svg>
            </div>
          </div>

          {/* Card 2: Square */}
          <div className="glass-panel bg-black/40 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-10 relative overflow-hidden group hover:border-[#8b5cf6]/50 transition-colors duration-500 flex flex-col justify-center items-center text-center">
            <div className="absolute inset-0 bg-gradient-to-br from-[#8b5cf6]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <Database size={40} className="text-[#8b5cf6] mb-6" />
            <h3 className="text-2xl font-bold text-white mb-4">Dữ Liệu Khổng Lồ</h3>
            <p className="text-[#94a3b8] leading-relaxed">Học hỏi từ 5+ năm dữ liệu tuyển sinh thực tế của hàng trăm trường ĐH.</p>
          </div>

          {/* Card 3: Square */}
          <div className="glass-panel bg-black/40 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-10 relative overflow-hidden group hover:border-[#f43f5e]/50 transition-colors duration-500">
             <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top_right,rgba(244,63,94,0.1),transparent_50%)]" />
             <LineChart size={40} className="text-[#f43f5e] mb-6" />
             <h3 className="text-2xl font-bold text-white mb-4">Dự Báo Chính Xác</h3>
             <p className="text-[#94a3b8] leading-relaxed">Thuật toán Machine Learning dự báo điểm chuẩn với sai số chỉ ±0.2 điểm.</p>
          </div>

          {/* Card 4: Large Wide */}
          <div className="md:col-span-2 glass-panel bg-black/40 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-10 relative overflow-hidden group hover:border-emerald-500/50 transition-colors duration-500">
            <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.02)_50%,transparent_75%)] bg-[length:250%_250%,100%_100%] animate-bg-pan" />
            <Bot size={40} className="text-emerald-400 mb-6 relative z-10" />
            <h3 className="text-3xl font-bold text-white mb-4 relative z-10">Chatbot Cố Vấn 24/7</h3>
            <p className="text-lg text-[#94a3b8] max-w-md leading-relaxed relative z-10">Giải đáp mọi thắc mắc về ngành nghề, học phí, môi trường học tập. Một "người anh đi trước" thực sự hiểu bạn.</p>
          </div>
        </div>
      </section>

      {/* --- CTA BANNER --- */}
      <section className="py-32 px-6 relative z-10 overflow-hidden mt-12">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black" />
        <div className="max-w-[1200px] mx-auto relative glass-panel bg-[#06b6d4]/5 border border-[#06b6d4]/20 rounded-[3rem] p-16 md:p-24 text-center overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(6,182,212,0.15),transparent_70%)]" />
          
          <h2 className="text-5xl md:text-7xl font-black tracking-tight text-white mb-8 relative z-10">
            Sẵn sàng chạm tay <br />vào <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-[#cbd5e1] drop-shadow-lg">ước mơ?</span>
          </h2>
          <p className="text-xl text-[#94a3b8] mb-12 max-w-2xl mx-auto font-medium relative z-10">
            Hàng chục ngàn học sinh đã tìm thấy bến đỗ vững chắc. Hãy là người tiếp theo làm chủ tương lai của mình.
          </p>
          <div className="relative z-10 flex justify-center">
            <HomeStartButton
              id="cta-start-btn-bottom"
              className="px-12 py-6 text-xl bg-white text-black font-extrabold hover:bg-[#cbd5e1] rounded-full shadow-[0_0_50px_rgba(255,255,255,0.3)] transition-all hover:scale-110"
            />
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
