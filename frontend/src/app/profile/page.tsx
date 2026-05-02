import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  Compass, FileText, Pencil, Palette, Users,
  Lightbulb, BookOpen, Crown, GraduationCap, Sparkles,
} from "lucide-react";

export const metadata: Metadata = {
  title: "SketchApp - Hồ sơ Năng lực số",
  description: "Phân tích đa chiều về tiềm năng cá nhân dựa trên các bài kiểm tra đánh giá năng lực và tư duy sáng tạo.",
};

const radarData = [
  { label: "Logic",    value: 85, angle: 0   },
  { label: "Ngôn ngữ",value: 65, angle: 60  },
  { label: "Sáng tạo",value: 78, angle: 120 },
  { label: "EQ",       value: 70, angle: 180 },
  { label: "Hợp tác", value: 82, angle: 240 },
  { label: "Lãnh đạo",value: 60, angle: 300 },
];

function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function RadarChart() {
  const cx = 200, cy = 200, maxR = 140;
  const levels = [0.25, 0.5, 0.75, 1];
  const dataPoints = radarData.map((d) => {
    const r = (d.value / 100) * maxR;
    return polarToCart(cx, cy, r, d.angle);
  });
  const pathD = dataPoints.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ") + " Z";

  return (
    <svg viewBox="0 0 400 400" className="radar-chart" role="img" aria-label="Radar chart — 6-dimension capability">
      {levels.map((l) => {
        const pts = radarData.map((d) => polarToCart(cx, cy, maxR * l, d.angle)).map((p) => `${p.x},${p.y}`).join(" ");
        return <polygon key={l} points={pts} fill="none" stroke="#2d2d2d" strokeWidth="1.5" opacity="0.2" />;
      })}
      {radarData.map((d) => {
        const end = polarToCart(cx, cy, maxR, d.angle);
        return <line key={d.label} x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="#2d2d2d" strokeWidth="1" opacity="0.15" />;
      })}
      <path d={pathD} fill="rgba(255,77,77,0.15)" stroke="#ff4d4d" strokeWidth="3" />
      {radarData.map((d, i) => {
        const lp = polarToCart(cx, cy, maxR + 28, d.angle);
        return (
          <g key={d.label}>
            <circle cx={dataPoints[i].x} cy={dataPoints[i].y} r="6" fill="#ff4d4d" stroke="#2d2d2d" strokeWidth="2" />
            <text x={lp.x} y={lp.y} textAnchor="middle" dominantBaseline="middle" style={{ fontFamily: "Kalam, cursive", fontSize: "14px", fontWeight: 700, fill: "#2d2d2d" }}>
              {d.label}
            </text>
            <text x={dataPoints[i].x} y={dataPoints[i].y - 14} textAnchor="middle" style={{ fontFamily: "Patrick Hand, cursive", fontSize: "13px", fontWeight: 700, fill: "#2d5da1" }}>
              {d.value}%
            </text>
          </g>
        );
      })}
    </svg>
  );
}

const statNotes = [
  { id: "stat-logic",      icon: Pencil,    label: "Logic (85%)",    desc: "Khả năng phân tích hệ thống và giải quyết vấn đề toán học." },
  { id: "stat-creative",   icon: Palette,   label: "Sáng tạo (78%)", desc: "Tư duy vượt giới hạn và tìm kiếm giải pháp mới." },
  { id: "stat-collab",     icon: Users,     label: "Hợp tác (82%)",  desc: "Kỹ năng làm việc nhóm và điều phối dự án." },
  { id: "stat-eq",         icon: Lightbulb, label: "EQ (70%)",       desc: "Trí tuệ cảm xúc và khả năng thấu hiểu người khác." },
  { id: "stat-language",   icon: BookOpen,  label: "Ngôn ngữ (65%)", desc: "Khả năng giao tiếp, viết lách và trình bày ý tưởng." },
  { id: "stat-leadership", icon: Crown,     label: "Lãnh đạo (60%)", desc: "Kỹ năng dẫn dắt, ra quyết định và truyền cảm hứng." },
];

const careerCards = [
  { id: "career-cs",   title: "Khoa học máy tính",  desc: "Phù hợp cao nhờ Logic mạnh và khả năng giải quyết vấn đề hệ thống.",             pct: 92, barClass: "bg-green-500",   rotate: "rotate-[1deg]" },
  { id: "career-data", title: "Phân tích dữ liệu",  desc: "Logic kết hợp tư duy hệ thống sẽ giúp bạn xử lý data hiệu quả.",               pct: 85, barClass: "bg-sketch-blue", rotate: "-rotate-[1deg]" },
  { id: "career-se",   title: "Kỹ thuật phần mềm",  desc: "Sáng tạo và Hợp tác cao là nền tảng tốt cho làm việc nhóm phát triển phần mềm.", pct: 80, barClass: "bg-sketch-blue", rotate: "rotate-[1deg]" },
];

export default function ProfilePage() {
  return (
    <>
      <Navbar />

      {/* Page Header */}
      <div id="profile-header" className="text-center px-8 py-12">
        <h1 className="text-sketch-red">Hồ sơ năng lực số của em</h1>
        <p className="text-sketch-muted text-xl max-w-xl mx-auto mt-2">
          Phân tích đa chiều về tiềm năng cá nhân của bạn dựa trên các bài kiểm tra đánh giá năng lực và tư duy sáng tạo.
        </p>
      </div>

      {/* ── Row 1: Radar | Stat Notes ── */}
      <section id="profile-content" className="px-8 pb-12 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">

          {/* Left — Radar Chart */}
          <div
            id="radar-section"
            className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 -rotate-[1deg] pinned"
          >
            <h2 className="flex items-center gap-2 mb-4 text-sketch-blue">
              <Compass size={24} /> Bản đồ Năng lực 6 Chiều
            </h2>
            <div className="flex justify-center">
              <RadarChart />
            </div>
          </div>

          {/* Right — Stat Notes (NO hover on container, only on individual items) */}
          <div
            id="stat-notes-section"
            className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 rotate-[1deg]"
          >
            <h3 className="flex items-center gap-2 mb-4 text-sketch-blue" style={{ fontSize: 22 }}>
              <FileText size={22} /> Ghi chú chỉ số
            </h3>
            <div className="flex flex-col divide-y divide-dashed divide-sketch-ink/20">
              {statNotes.map(({ id, icon: Icon, label, desc }) => (
                /* ✅ Hover ONLY on this individual item — not the container */
                <div
                  key={id}
                  id={id}
                  className={`rounded-lg cursor-default transition-all duration-150 hover:bg-blue-50 hover:-translate-y-px`}
                  style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "12px" }}
                >
                  <div style={{ marginTop: 2, color: "#2d5da1", flexShrink: 0 }}>
                    <Icon size={22} />
                  </div>
                  <div>
                    <p style={{ fontFamily: "Kalam, cursive", fontSize: 15, fontWeight: 700, color: "#2d5da1", marginBottom: 2 }}>
                      {label}
                    </p>
                    <p style={{ color: "#8f6f6d", fontSize: 14, lineHeight: 1.4 }}>{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Divider ── */}
      <hr className="hand-drawn-hr" />

      {/* ── Row 2: Career Suggestions ── */}
      <section id="career-suggestions" className="px-8 py-12 max-w-6xl mx-auto">
        <h2 className="text-center mb-10 flex items-center justify-center gap-2 -rotate-[0.5deg]">
          <GraduationCap size={28} /> Gợi ý Nhóm ngành
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {careerCards.map(({ id, title, desc, pct, barClass, rotate }) => (
            /* ✅ Hover on each individual career card */
            <div
              key={id}
              id={id}
              className={`relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 tape transition-all duration-200 hover:-translate-y-1.5 hover:shadow-sketch-lg cursor-pointer ${rotate}`}
            >
              <h3 className="text-sketch-blue mb-2">{title}</h3>
              <p className="text-sketch-muted text-base mb-4">{desc}</p>
              <div className="h-3 border-[2px] border-sketch-ink rounded-full overflow-hidden bg-sketch-surface-dim">
                <div className={`h-full rounded-full transition-all duration-700 ${barClass}`} style={{ width: `${pct}%` }} />
              </div>
              <p className="text-sm text-sketch-muted mt-1.5">Phù hợp: {pct}%</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Quote ── */}
      <section id="profile-quote" className="px-8 pb-16 max-w-3xl mx-auto">
        <div className="animate-float bg-sketch-yellow border-[2px] border-sketch-ink rounded-2xl p-6 text-center rotate-[0.5deg] shadow-sketch flex items-center justify-center gap-3">
          <Sparkles size={22} className="text-sketch-red flex-shrink-0" />
          <span style={{ fontFamily: "var(--font-heading)", fontSize: 20 }}>
            &ldquo;Tiềm năng của bạn là vô hạn, hãy bắt đầu từ những thế mạnh sẵn có!&rdquo;
          </span>
          <Sparkles size={22} className="text-sketch-red flex-shrink-0" />
        </div>
      </section>

      <Footer />
    </>
  );
}
