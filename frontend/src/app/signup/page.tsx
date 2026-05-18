import type { Metadata } from "next";
import Link from "next/link";
import SignUpForm from "./SignUpForm";
import Navbar from "@/components/Navbar";
import { Sparkles, ArrowRight, UserPlus } from "lucide-react";

export const metadata: Metadata = {
  title: "SketchApp - Sign Up",
  description: "Tạo tài khoản SketchApp và bắt đầu hành trình sáng tạo của bạn.",
};

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-[#030014] text-white overflow-hidden flex flex-col relative selection:bg-[#c084fc]/30">
      <Navbar />
      
      {/* Dynamic Background */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-20 [mask-image:linear-gradient(180deg,white,transparent)]"></div>
      <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-[#c084fc] opacity-10 blur-[150px] rounded-full animate-float-smooth pointer-events-none"></div>
      <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-[#06b6d4] opacity-10 blur-[150px] rounded-full animate-pulse-glow pointer-events-none"></div>

      {/* Main Content Center */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 relative z-10 mt-12">
        <div
          id="signup-card"
          className="w-full max-w-4xl glass-panel bg-black/40 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] px-8 py-12 sm:px-16 sm:py-16 shadow-[0_20px_80px_rgba(0,0,0,0.6)] relative overflow-hidden"
        >
          {/* Decorative Corner Glows */}
          <div className="absolute top-0 left-0 w-32 h-32 bg-[#c084fc]/20 blur-3xl rounded-full"></div>
          <div className="absolute bottom-0 right-0 w-40 h-40 bg-[#06b6d4]/20 blur-3xl rounded-full"></div>

          <div className="relative z-10 flex flex-col items-center mb-12">
             <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#c084fc]/20 to-[#06b6d4]/20 border border-[#c084fc]/30 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(192,132,252,0.3)]">
               <UserPlus size={32} className="text-[#c084fc]" />
             </div>
             <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white to-[#94a3b8] mb-3 text-center">
               Thiết Lập Hồ Sơ Định Hướng
             </h1>
             <p className="flex items-center justify-center gap-2 text-center text-[#94a3b8] text-lg font-medium">
               Bước đầu tiên để khai phá lộ trình nghề nghiệp tương lai <Sparkles size={16} className="text-[#f59e0b]" />
             </p>
          </div>

          <SignUpForm />

          <div className="mt-12 pt-8 border-t border-white/10 flex flex-col items-center relative z-10">
            <p className="text-center text-[#94a3b8]">
              Đã sở hữu hồ sơ năng lực?{" "}
              <Link href="/login" id="signup-login-link" className="text-white font-bold hover:text-[#c084fc] transition-colors inline-flex items-center gap-1 group">
                Truy cập ngay <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </Link>
            </p>

            <div className="flex justify-center gap-6 mt-8 text-xs text-[#94a3b8]/70 font-medium">
              <Link href="#" className="hover:text-white transition-colors">Bảo mật</Link>
              <Link href="#" className="hover:text-white transition-colors">Điều khoản</Link>
              <Link href="#" className="hover:text-white transition-colors">Hỗ trợ</Link>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
