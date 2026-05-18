

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  Brain,
  CheckCircle2,
  Compass,
  GraduationCap,
  LoaderCircle,
  Mail,
  MapPin,
  NotebookTabs,
  RefreshCw,
  Sparkles,
  Target,
  UserRound,
  Zap,
} from "lucide-react";
import {
  ApiError,
  DigitalCompetencyProfile,
  RadarAxis,
  RiasecGroup,
  RiasecScore,
  Student,
  clearAuthSession,
  getAccessToken,
  getLatestRiasecProfile,
  getMe,
  getRiasecProfile,
  getStoredStudent,
} from "@/lib/api";
import { InfoPill } from './components/InfoPill';
import { ScoreBars } from './components/ScoreBars';
import { RiasecRadar } from './components/RiasecRadar';
import { RiasecResultSummary } from './components/RiasecResultSummary';

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];

const groupColors: Record<RiasecGroup, string> = {
  R: "#f43f5e",
  I: "#06b6d4",
  A: "#c084fc",
  S: "#10b981",
  E: "#f59e0b",
  C: "#94a3b8",
};

function formatDate(value?: string | null) {
  if (!value) return "Chưa cập nhật";
  return new Intl.DateTimeFormat("vi-VN").format(new Date(value));
}

function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

export default function ProfileClient() {
  const searchParams = useSearchParams();
  const dcpId = searchParams.get("dcp_id");
  const [student, setStudent] = useState<Student | null>(null);
  const [riasecProfile, setRiasecProfile] = useState<DigitalCompetencyProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isResultLoading, setIsResultLoading] = useState(false);
  const [error, setError] = useState("");
  const [resultError, setResultError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      setIsLoading(true);
      setError("");

      try {
        const stored = getStoredStudent();
        if (stored) {
          setStudent(stored);
        }

        if (!getAccessToken()) {
          throw new ApiError("Bạn cần đăng nhập để xem hồ sơ.", 401, null);
        }

        const currentStudent = await getMe();
        setStudent(currentStudent);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          clearAuthSession();
          setError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại để xem hồ sơ.");
        } else {
          setError("Không thể tải hồ sơ học sinh. Vui lòng thử lại.");
        }
      } finally {
        setIsLoading(false);
      }
    }

    void loadProfile();
  }, []);

  useEffect(() => {
    async function loadRiasecResult() {
      if (!getAccessToken()) {
        return;
      }

      setIsResultLoading(true);
      setResultError("");
      setRiasecProfile(null);

      try {
        const result = dcpId
          ? await getRiasecProfile(dcpId)
          : await getLatestRiasecProfile();
        setRiasecProfile(result);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404 && !dcpId) {
          return;
        }

        setResultError("Không thể tải kết quả RIASEC. Vui lòng mở lại từ bài đánh giá hoặc làm lại RIASEC.");
      } finally {
        setIsResultLoading(false);
      }
    }

    void loadRiasecResult();
  }, [dcpId]);

  return (
    <div className="bg-[#030014] text-white min-h-screen relative overflow-hidden">
      {/* Immersive Background */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[800px] h-[800px] bg-[radial-gradient(circle,rgba(6,182,212,0.1),transparent_60%)]"></div>
        <div className="absolute top-[40%] right-[-20%] w-[1000px] h-[1000px] bg-[radial-gradient(circle,rgba(124,58,237,0.05),transparent_60%)]"></div>
      </div>
      
      <div className="relative z-50">
        <Navbar />
      </div>

      <main className="px-5 md:px-8 py-16 max-w-7xl mx-auto relative z-10">
        
        {/* Loading & Error States */}
        {(isLoading || error) && (
          <section className="mb-12 text-center">
            {isLoading && (
              <div className="inline-flex items-center gap-3 border border-white/10 glass-panel px-6 py-4 rounded-2xl font-bold text-[#06b6d4] shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
                <LoaderCircle size={20} className="animate-spin" /> Đang đồng bộ hồ sơ hệ thống...
              </div>
            )}
            {error && (
              <div className="mx-auto max-w-2xl border border-[#f43f5e]/30 bg-[#f43f5e]/10 p-6 rounded-2xl shadow-[0_10px_30px_rgba(244,63,94,0.15)] flex flex-col items-center justify-center gap-4 text-center">
                <div className="flex items-center justify-center gap-3 font-bold text-[#f43f5e] text-lg">
                  <AlertTriangle size={24} /> {error}
                </div>
                <Link href="/login" className="btn-premium px-6 py-2 mt-2">
                  Đi tới đăng nhập
                </Link>
              </div>
            )}
          </section>
        )}

        {/* Dashboard Profile Card (Logged In) */}
        {student && !error && (
          <section className="mb-16 animate-[slideUp_0.8s_ease-out_forwards] opacity-0" style={{ animationFillMode: 'forwards' }}>
            <div className="glass-panel border border-white/10 rounded-[2.5rem] overflow-hidden bg-black/40 backdrop-blur-2xl relative shadow-[0_20px_50px_rgba(0,0,0,0.5)] group">
               {/* Premium Cover Gradient */}
               <div className="h-48 md:h-64 w-full bg-gradient-to-r from-[#7c3aed]/30 via-[#06b6d4]/30 to-[#f59e0b]/30 relative overflow-hidden transition-all duration-700 group-hover:scale-105">
                  <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px]"></div>
                  <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 blur-[80px] rounded-full mix-blend-overlay"></div>
               </div>
               
               {/* Profile Info Container */}
               <div className="px-8 md:px-12 pb-12 relative -mt-20 md:-mt-24">
                  <div className="flex flex-col md:flex-row gap-8 items-start md:items-end mb-12">
                     <div className="w-32 h-32 md:w-40 md:h-40 rounded-3xl bg-black border-4 border-[#030014] flex items-center justify-center text-6xl font-black text-white relative overflow-hidden shadow-2xl shrink-0 transition-transform duration-500 hover:scale-105 hover:rotate-2">
                        <div className="absolute inset-0 bg-gradient-to-br from-[#06b6d4] to-[#7c3aed] opacity-80"></div>
                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-20 mix-blend-overlay"></div>
                        <span className="relative z-10 drop-shadow-md">{student.full_name.charAt(0).toUpperCase()}</span>
                     </div>
                     <div className="flex-1">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/5 border border-white/10 rounded-full text-xs font-bold text-white/80 uppercase tracking-wider mb-4 shadow-sm backdrop-blur-md">
                          <Sparkles size={14} className="text-[#06b6d4]" /> Học viên SketchApp
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-3 flex items-center gap-3">
                          {student.full_name}
                          {student.is_verified && <CheckCircle2 size={28} className="text-[#06b6d4]" />}
                        </h1>
                        <p className="text-[#94a3b8] text-lg max-w-2xl leading-relaxed">
                          Hệ thống quản lý thông tin cá nhân và lưu trữ kết quả phân tích năng lực lõi, giúp AI đưa ra lộ trình nghề nghiệp chính xác nhất.
                        </p>
                     </div>
                     <div className="shrink-0 hidden md:block">
                         <button className="btn-glass px-6 py-3 inline-flex items-center gap-2 opacity-50 cursor-not-allowed">
                            Chỉnh sửa hồ sơ
                         </button>
                     </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    <InfoPill icon={Mail} label="Email" value={student.email} colorClass="bg-blue-500/10 text-blue-400 border-blue-500/20" />
                    <InfoPill icon={MapPin} label="Khu vực" value={`${student.province} - ${student.area_code}`} colorClass="bg-purple-500/10 text-purple-400 border-purple-500/20" />
                    <InfoPill icon={Target} label="Tỉnh mục tiêu" value={student.target_province ?? "Chưa cập nhật"} colorClass="bg-rose-500/10 text-rose-400 border-rose-500/20" />
                    <InfoPill icon={BookOpen} label="Ngày sinh" value={formatDate(student.dob)} colorClass="bg-emerald-500/10 text-emerald-400 border-emerald-500/20" />
                    <InfoPill icon={GraduationCap} label="Nhóm ưu tiên" value={student.priority_group ?? "Không có"} colorClass="bg-amber-500/10 text-amber-400 border-amber-500/20" />
                    <InfoPill icon={UserRound} label="Trạng thái" value={student.is_verified ? "Đã xác thực" : "Chưa xác thực"} colorClass="bg-cyan-500/10 text-cyan-400 border-cyan-500/20" />
                  </div>
               </div>
            </div>
          </section>
        )}

        {/* Guest View */}
        {!student && !isLoading && !error && (
          <section className="mb-16 animate-[slideUp_0.8s_ease-out_forwards] opacity-0" style={{ animationFillMode: 'forwards' }}>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-7xl font-black mb-6 tracking-tight">
                Hồ sơ định hướng <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-[#06b6d4]">của bạn</span>
              </h1>
              <p className="text-[#94a3b8] text-xl max-w-3xl mx-auto leading-relaxed">
                Hệ thống quản lý thông tin cá nhân và lưu trữ kết quả phân tích năng lực lõi, giúp AI đưa ra lộ trình nghề nghiệp chính xác nhất.
              </p>
            </div>
            
            <div className="mx-auto border border-white/10 glass-panel rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] p-10 max-w-3xl bg-black/40 backdrop-blur-xl text-center">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6">
                <UserRound size={40} className="text-[#06b6d4]" />
              </div>
              <h2 className="text-3xl font-bold mb-4">Khách viếng thăm</h2>
              <p className="text-[#94a3b8] text-lg mb-8 max-w-xl mx-auto">
                Đăng nhập để hệ thống lưu hồ sơ, kết quả đánh giá RIASEC và xây dựng lộ trình học tập độc quyền cho bạn.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link href="/login" className="btn-premium px-8 py-3 text-lg">
                  Đăng nhập ngay
                </Link>
                <Link href="/signup" className="btn-glass px-8 py-3 text-lg">
                  Tạo tài khoản
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* RIASEC Result Display */}
        {isResultLoading && (
          <div className="w-full glass-panel border border-[#06b6d4]/30 bg-gradient-to-br from-[#06b6d4]/5 to-[#7c3aed]/10 p-16 rounded-[2.5rem] text-center shadow-[0_0_50px_rgba(6,182,212,0.15)] mb-16 animate-[slideUp_0.8s_ease-out_forwards] opacity-0" style={{ animationFillMode: 'forwards' }}>
            <LoaderCircle size={40} className="animate-spin text-[#06b6d4] mx-auto mb-6" />
            <h3 className="text-2xl font-bold text-white mb-2">Đang tải báo cáo năng lực</h3>
            <p className="text-[#94a3b8]">Đang giải mã dữ liệu radar từ máy chủ...</p>
          </div>
        )}

        {resultError && !isResultLoading && (
          <div className="w-full glass-panel border border-[#f43f5e]/30 bg-[#f43f5e]/10 p-10 rounded-[2.5rem] flex flex-col items-center justify-center text-center shadow-[0_20px_50px_rgba(244,63,94,0.15)] mb-16 animate-[slideUp_0.8s_ease-out_forwards] opacity-0" style={{ animationFillMode: 'forwards' }}>
            <AlertTriangle size={36} className="text-[#f43f5e] mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Lỗi truy xuất dữ liệu</h3>
            <p className="text-[#94a3b8] mb-6">{resultError}</p>
            <Link href="/chat" className="btn-premium px-8 py-3">Làm lại RIASEC</Link>
          </div>
        )}

        {!isResultLoading && riasecProfile && (
           <div className="mt-8">
             <RiasecResultSummary profile={riasecProfile} />
           </div>
        )}

        {/* Next Steps */}
        <section className="mb-10 animate-[slideUp_0.8s_ease-out_0.4s_forwards] opacity-0" style={{ animationFillMode: 'forwards' }}>
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center border border-white/20">
                <Compass size={16} className="text-white"/>
              </div>
              Lộ trình Hệ thống
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <div className="glass-panel border border-white/10 rounded-3xl p-8 bg-gradient-to-br from-[#7c3aed]/10 to-transparent relative overflow-hidden group hover:border-[#7c3aed]/50 transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(124,58,237,0.2)]">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#7c3aed] opacity-20 blur-3xl group-hover:opacity-40 transition-opacity"></div>
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-3 relative z-10">
                <span className="w-10 h-10 rounded-full bg-[#7c3aed]/20 flex items-center justify-center text-[#c084fc] border border-[#7c3aed]/30 shadow-[0_0_15px_rgba(124,58,237,0.3)]">1</span>
                Phân tích RIASEC
              </h3>
              <p className="text-[#94a3b8] mb-8 relative z-10 text-lg">
                Tương tác với AI qua các tình huống giả định để hệ thống giải mã bản đồ năng lực bẩm sinh của bạn.
              </p>
              <Link href="/chat" className="inline-flex items-center gap-2 font-bold text-[#c084fc] hover:text-white transition-colors relative z-10">
                Bắt đầu đánh giá <Sparkles size={16} />
              </Link>
            </div>

            <div className="glass-panel border border-white/10 rounded-3xl p-8 bg-gradient-to-br from-[#06b6d4]/10 to-transparent relative overflow-hidden group hover:border-[#06b6d4]/50 transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(6,182,212,0.2)]">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#06b6d4] opacity-20 blur-3xl group-hover:opacity-40 transition-opacity"></div>
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-3 relative z-10">
                <span className="w-10 h-10 rounded-full bg-[#06b6d4]/20 flex items-center justify-center text-[#06b6d4] border border-[#06b6d4]/30 shadow-[0_0_15px_rgba(6,182,212,0.3)]">2</span>
                Khám phá Ngành
              </h3>
              <p className="text-[#94a3b8] relative z-10 text-lg">
                Dựa trên báo cáo RIASEC, hệ thống đối chiếu với kho dữ liệu để đưa ra các gợi ý nhóm ngành nghề phù hợp nhất.
              </p>
            </div>

            <div className="glass-panel border border-white/10 rounded-3xl p-8 bg-gradient-to-br from-[#f59e0b]/10 to-transparent relative overflow-hidden group hover:border-[#f59e0b]/50 transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(245,158,11,0.2)]">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#f59e0b] opacity-20 blur-3xl group-hover:opacity-40 transition-opacity"></div>
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-3 relative z-10">
                <span className="w-10 h-10 rounded-full bg-[#f59e0b]/20 flex items-center justify-center text-[#f59e0b] border border-[#f59e0b]/30 shadow-[0_0_15px_rgba(245,158,11,0.3)]">3</span>
                La bàn Tuyển sinh
              </h3>
              <p className="text-[#94a3b8] mb-8 relative z-10 text-lg">
                Dự đoán chính xác cơ hội đỗ đại học dựa trên năng lực, điểm chuẩn lịch sử và xu hướng ngành nghề.
              </p>
              <Link href="/admission" className="inline-flex items-center gap-2 font-bold text-[#f59e0b] hover:text-white transition-colors relative z-10">
                Khám phá La bàn <Compass size={16} />
              </Link>
            </div>

          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
}

