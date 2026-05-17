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
  getMe,
  getRiasecProfile,
  getStoredStudent,
} from "@/lib/api";

const previewRadar = [
  { label: "RIASEC", value: 0.18, angle: 0 },
  { label: "Học lực", value: 0.34, angle: 60 },
  { label: "Ngành", value: 0.22, angle: 120 },
  { label: "Tuyển sinh", value: 0.16, angle: 180 },
  { label: "Kế hoạch", value: 0.28, angle: 240 },
  { label: "Hồ sơ", value: 0.42, angle: 300 },
];

function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function ProfileMapPreview() {
  const cx = 180;
  const cy = 180;
  const maxR = 120;
  const levels = [0.25, 0.5, 0.75, 1];
  const points = previewRadar.map((item) => polarToCart(cx, cy, item.value * maxR, item.angle));
  const pathD = `${points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ")} Z`;

  return (
    <svg viewBox="0 0 360 360" className="w-full max-w-[360px] aspect-square" role="img" aria-label="Bản đồ hồ sơ định hướng">
      {levels.map((level) => {
        const pts = previewRadar
          .map((item) => polarToCart(cx, cy, maxR * level, item.angle))
          .map((point) => `${point.x},${point.y}`)
          .join(" ");

        return <polygon key={level} points={pts} fill="none" stroke="#2d2d2d" strokeWidth="1.5" opacity="0.18" />;
      })}

      {previewRadar.map((item, index) => {
        const end = polarToCart(cx, cy, maxR, item.angle);
        const label = polarToCart(cx, cy, maxR + 32, item.angle);
        const point = points[index];

        return (
          <g key={item.label}>
            <line x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="#2d2d2d" strokeWidth="1" opacity="0.12" />
            <circle cx={point.x} cy={point.y} r="5" fill="#ff4d4d" stroke="#2d2d2d" strokeWidth="2" />
            <text
              x={label.x}
              y={label.y}
              textAnchor="middle"
              dominantBaseline="middle"
              style={{ fontFamily: "Kalam, cursive", fontSize: 14, fontWeight: 700, fill: "#2d5da1" }}
            >
              {item.label}
            </text>
          </g>
        );
      })}

      <path d={pathD} fill="rgba(255,77,77,0.14)" stroke="#ff4d4d" strokeWidth="3" />
    </svg>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "Chưa cập nhật";
  }

  return new Intl.DateTimeFormat("vi-VN").format(new Date(value));
}

function InfoPill({ icon: Icon, label, value }: { icon: typeof UserRound; label: string; value: string }) {
  return (
    <div className="border-[2px] border-sketch-ink bg-sketch-surface rounded-lg p-4">
      <div className="flex items-center gap-2 text-sketch-blue font-bold mb-1">
        <Icon size={18} /> {label}
      </div>
      <p className="text-sketch-ink">{value}</p>
    </div>
  );
}

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];

const groupColors: Record<RiasecGroup, string> = {
  R: "#ff4d4d",
  I: "#2d5da1",
  A: "#7c3aed",
  S: "#16a34a",
  E: "#ea580c",
  C: "#64748b",
};

function ScoreBars({ scores }: { scores: RiasecScore }) {
  const maxScore = Math.max(1, ...riasecGroups.map((group) => scores[group] ?? 0));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {riasecGroups.map((group) => {
        const value = scores[group] ?? 0;
        const width = `${Math.max(5, (value / maxScore) * 100)}%`;

        return (
          <div key={group} className="flex items-center gap-3">
            <span
              className="w-8 h-8 inline-flex items-center justify-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow font-bold"
              style={{ fontFamily: "var(--font-heading)", color: groupColors[group] }}
            >
              {group}
            </span>
            <div className="flex-1 h-4 border-[2px] border-sketch-ink rounded-full overflow-hidden bg-sketch-surface-dim">
              <div className="h-full" style={{ width, backgroundColor: groupColors[group] }} />
            </div>
            <span className="min-w-10 text-right text-sm font-bold">{value.toFixed(1)}</span>
          </div>
        );
      })}
    </div>
  );
}

function RiasecRadar({ axes }: { axes: RadarAxis[] }) {
  const cx = 180;
  const cy = 180;
  const maxR = 118;
  const levels = [0.25, 0.5, 0.75, 1];
  const normalizedAxes = riasecGroups.map((group, index) => {
    const axis = axes.find((item) => item.group === group);
    return {
      group,
      value: axis?.normalized_score ?? 0,
      angle: index * 60,
    };
  });
  const dataPoints = normalizedAxes.map((axis) =>
    polarToCart(cx, cy, (axis.value / 100) * maxR, axis.angle),
  );
  const pathD = `${dataPoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ")} Z`;

  return (
    <svg viewBox="0 0 360 360" className="w-full max-w-[320px] aspect-square" role="img" aria-label="Biểu đồ radar RIASEC">
      {levels.map((level) => {
        const pts = normalizedAxes
          .map((axis) => polarToCart(cx, cy, maxR * level, axis.angle))
          .map((point) => `${point.x},${point.y}`)
          .join(" ");

        return <polygon key={level} points={pts} fill="none" stroke="#2d2d2d" strokeWidth="1.5" opacity="0.18" />;
      })}

      {normalizedAxes.map((axis) => {
        const end = polarToCart(cx, cy, maxR, axis.angle);
        const label = polarToCart(cx, cy, maxR + 30, axis.angle);

        return (
          <g key={axis.group}>
            <line x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="#2d2d2d" strokeWidth="1" opacity="0.14" />
            <text
              x={label.x}
              y={label.y}
              textAnchor="middle"
              dominantBaseline="middle"
              style={{ fontFamily: "Kalam, cursive", fontSize: 15, fontWeight: 700, fill: groupColors[axis.group] }}
            >
              {axis.group}
            </text>
          </g>
        );
      })}

      <path d={pathD} fill="rgba(45,93,161,0.16)" stroke="#2d5da1" strokeWidth="3" />
      {dataPoints.map((point, index) => {
        const axis = normalizedAxes[index];

        return <circle key={axis.group} cx={point.x} cy={point.y} r="6" fill={groupColors[axis.group]} stroke="#2d2d2d" strokeWidth="2" />;
      })}
    </svg>
  );
}

function RiasecResultSummary({ profile }: { profile: DigitalCompetencyProfile }) {
  const axes = profile.radar_chart?.axes ?? [];
  const dominantGroups = profile.dominant_groups ?? [];
  const groupAnalysis = profile.group_analysis ?? [];
  const recommendations = profile.career_recommendations;

  return (
    <section className="mb-10 border-[2px] border-sketch-ink bg-sketch-yellow wobbly shadow-sketch-md p-5 md:p-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 border-[2px] border-sketch-ink bg-sketch-surface rounded-full font-bold text-sketch-blue">
            <Sparkles size={18} /> Kết quả RIASEC mới nhất
          </div>
          <h2 className="mt-3 text-sketch-red" style={{ fontSize: 34 }}>
            {profile.riasec_code}
          </h2>
          <p className="max-w-4xl text-sketch-ink">{profile.summary}</p>
        </div>
        <Link href="/chat" className="inline-flex items-center justify-center gap-2 px-4 py-2 border-[2px] border-sketch-ink bg-sketch-surface wobbly-btn shadow-sketch text-sketch-blue">
          <RefreshCw size={16} /> Làm lại RIASEC
        </Link>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[360px_1fr] gap-5">
        <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 font-bold text-sketch-blue">
            <BarChart3 size={18} /> Radar chart
          </div>
          <div className="flex justify-center">
            <RiasecRadar axes={axes} />
          </div>
          <ScoreBars scores={profile.scores} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
            <h3 className="text-sketch-blue flex items-center gap-2 mb-3" style={{ fontSize: 22 }}>
              <Target size={18} /> Nhóm nổi bật
            </h3>
            <div className="space-y-3">
              {dominantGroups.slice(0, 3).map((group) => (
                <div key={group.group} className="border-[2px] border-sketch-ink bg-sketch-bg p-3 rounded-lg">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold" style={{ color: groupColors[group.group] }}>
                      {group.group} - {group.label}
                    </span>
                    <span className="text-sm font-bold">{group.score.toFixed(1)} điểm</span>
                  </div>
                  <p className="text-sm text-sketch-muted mt-1">{group.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
            <h3 className="text-sketch-blue flex items-center gap-2 mb-3" style={{ fontSize: 22 }}>
              <GraduationCap size={18} /> Ngành phù hợp
            </h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {(recommendations?.recommended_majors ?? profile.recommended_majors).slice(0, 8).map((major) => (
                <span key={major} className="px-3 py-1 border-[2px] border-sketch-ink bg-sketch-yellow rounded-full text-sm font-bold">
                  {major}
                </span>
              ))}
            </div>
            <p className="text-sm text-sketch-muted">
              Vai trò gợi ý: {(recommendations?.suitable_roles ?? []).slice(0, 6).join(", ") || "Đang cập nhật."}
            </p>
          </div>

          <div className="lg:col-span-2 bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
            <h3 className="text-sketch-blue flex items-center gap-2 mb-3" style={{ fontSize: 22 }}>
              <Brain size={18} /> Phân tích nhóm
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {groupAnalysis.slice(0, 3).map((group) => (
                <div key={group.group} className="border-[2px] border-sketch-ink bg-sketch-bg p-3 rounded-lg">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-bold" style={{ color: groupColors[group.group] }}>
                      {group.group} - {group.label}
                    </span>
                    <span className="text-xs uppercase font-bold text-sketch-muted">{group.level}</span>
                  </div>
                  <p className="text-sm text-sketch-muted mb-2">{group.description}</p>
                  <p className="text-sm">
                    <b>Kỹ năng:</b> {group.digital_competencies.slice(0, 3).join(", ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function ProfileClient() {
  const searchParams = useSearchParams();
  const dcpId = searchParams.get("dcp_id");
  const [student, setStudent] = useState<Student | null>(() => getStoredStudent());
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
      if (!dcpId || !getAccessToken()) {
        return;
      }

      setIsResultLoading(true);
      setResultError("");

      try {
        const result = await getRiasecProfile(dcpId);
        setRiasecProfile(result);
      } catch {
        setResultError("Không thể tải kết quả RIASEC. Vui lòng mở lại từ bài đánh giá hoặc làm lại RIASEC.");
      } finally {
        setIsResultLoading(false);
      }
    }

    void loadRiasecResult();
  }, [dcpId]);

  return (
    <>
      <Navbar />

      <main className="px-5 md:px-8 py-10 max-w-7xl mx-auto">
        <section className="grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-8 items-start">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 border-[2px] border-sketch-ink bg-sketch-yellow rounded-full font-bold text-sketch-ink mb-4">
              <NotebookTabs size={18} /> Hồ sơ học sinh
            </div>

            <h1 className="text-sketch-red mb-3">
              {student?.full_name ? `Xin chào, ${student.full_name}` : "Hồ sơ định hướng của bạn"}
            </h1>
            <p className="text-sketch-muted text-xl max-w-3xl">
              Đây là nơi gom thông tin cá nhân, kết quả RIASEC và các bước tiếp theo để hệ thống gợi ý ngành học chính xác hơn.
            </p>

            {isLoading && (
              <div className="mt-6 inline-flex items-center gap-2 border-[2px] border-sketch-ink bg-sketch-surface px-4 py-3 shadow-sketch rounded-lg font-bold text-sketch-blue">
                <LoaderCircle size={18} className="animate-spin" /> Đang tải hồ sơ...
              </div>
            )}

            {error && (
              <div className="mt-6 border-[2px] border-sketch-error bg-red-50 p-4 shadow-sketch rounded-lg">
                <div className="flex items-center gap-2 font-bold text-sketch-error mb-2">
                  <AlertTriangle size={18} /> {error}
                </div>
                <Link href="/login" className="text-sketch-blue">
                  Đi tới đăng nhập
                </Link>
              </div>
            )}
          </div>

          <aside className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-5 pinned">
            <h2 className="flex items-center gap-2 text-sketch-blue mb-3" style={{ fontSize: 26 }}>
              <Compass size={24} /> Bản đồ hồ sơ
            </h2>
            <ProfileMapPreview />
            <p className="text-sm text-sketch-muted mt-2">
              Biểu đồ này là preview workflow. Kết quả RIASEC thật sẽ nằm trong màn hội thoại sau khi bạn hoàn tất bài đánh giá.
            </p>
          </aside>
        </section>

        <hr className="hand-drawn-hr" />

        {student ? (
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-10">
            <InfoPill icon={Mail} label="Email" value={student.email} />
            <InfoPill icon={MapPin} label="Khu vực" value={`${student.province} - ${student.area_code}`} />
            <InfoPill icon={Target} label="Tỉnh mục tiêu" value={student.target_province ?? "Chưa cập nhật"} />
            <InfoPill icon={BookOpen} label="Ngày sinh" value={formatDate(student.dob)} />
            <InfoPill icon={GraduationCap} label="Nhóm ưu tiên" value={student.priority_group ?? "Không có"} />
            <InfoPill icon={CheckCircle2} label="Trạng thái" value={student.is_verified ? "Đã xác thực" : "Chưa xác thực"} />
          </section>
        ) : (
          <section className="mb-10 border-[2px] border-sketch-ink bg-sketch-surface wobbly shadow-sketch-md p-6 max-w-3xl">
            <h2 className="text-sketch-blue flex items-center gap-2 mb-3" style={{ fontSize: 26 }}>
              <UserRound size={24} /> Bạn chưa đăng nhập
            </h2>
            <p className="text-sketch-muted mb-5">
              Đăng nhập để hệ thống lưu hồ sơ, kết quả RIASEC và các gợi ý ngành học theo đúng tài khoản của bạn.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/login" className="inline-flex items-center gap-2 px-5 py-2 border-[2px] border-sketch-ink bg-sketch-red text-white wobbly-btn shadow-sketch">
                Đăng nhập
              </Link>
              <Link href="/signup" className="inline-flex items-center gap-2 px-5 py-2 border-[2px] border-sketch-ink bg-sketch-yellow text-sketch-ink wobbly-btn shadow-sketch">
                Tạo tài khoản
              </Link>
            </div>
          </section>
        )}

        {isResultLoading && (
          <section className="mb-10 inline-flex items-center gap-2 border-[2px] border-sketch-ink bg-sketch-surface px-4 py-3 shadow-sketch rounded-lg font-bold text-sketch-blue">
            <LoaderCircle size={18} className="animate-spin" /> Đang tải kết quả RIASEC...
          </section>
        )}

        {resultError && (
          <section className="mb-10 border-[2px] border-sketch-error bg-red-50 p-4 shadow-sketch rounded-lg">
            <div className="flex items-center gap-2 font-bold text-sketch-error">
              <AlertTriangle size={18} /> {resultError}
            </div>
          </section>
        )}

        {riasecProfile && <RiasecResultSummary profile={riasecProfile} />}

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-5 tape">
            <h3 className="text-sketch-blue flex items-center gap-2 mb-3">
              <Compass size={22} /> 1. Làm RIASEC
            </h3>
            <p className="text-sketch-muted mb-4">
              Trả lời các tình huống ngắn để hệ thống xác định nhóm Holland Code nổi bật.
            </p>
            <Link href="/chat" className="inline-flex items-center gap-2 px-4 py-2 border-[2px] border-sketch-ink bg-sketch-red text-white wobbly-btn shadow-sketch">
              Bắt đầu đánh giá
            </Link>
          </div>

          <div className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-5 tape rotate-[0.5deg]">
            <h3 className="text-sketch-blue flex items-center gap-2 mb-3">
              <GraduationCap size={22} /> 2. Xem ngành phù hợp
            </h3>
            <p className="text-sketch-muted">
              Sau khi hoàn tất RIASEC, hệ thống trả radar chart, nhóm nổi bật, ngành học, vai trò nghề nghiệp và kỹ năng nên phát triển.
            </p>
          </div>

          <div className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-5 tape -rotate-[0.5deg]">
            <h3 className="text-sketch-blue flex items-center gap-2 mb-3">
              <Sparkles size={22} /> 3. Đối chiếu tuyển sinh
            </h3>
            <p className="text-sketch-muted mb-4">
              Khi có điểm học tập và RIASEC, phần la bàn tuyển sinh sẽ giúp so sánh lựa chọn an toàn, vừa sức và tham vọng.
            </p>
            <Link href="/admission" className="text-sketch-blue">
              Xem la bàn tuyển sinh
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
