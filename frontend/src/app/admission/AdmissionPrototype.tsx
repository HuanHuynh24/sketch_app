"use client";

import { useMemo, useState } from "react";
import Navbar from "@/components/Navbar";
import {
  ArrowLeft,
  ArrowRight,
  Bot,
  ChevronDown,
  ChevronsUp,
  CircleDollarSign,
  ClipboardList,
  Gauge,
  GraduationCap,
  MapPin,
  Search,
  SendHorizontal,
  ShieldCheck,
  SlidersHorizontal,
  X,
  Zap,
} from "lucide-react";

type Tier = "safe" | "balance" | "challenge";

interface UniversityOption {
  id: string;
  tier: Tier;
  university: string;
  shortName: string;
  major: string;
  location: string;
  combo: string;
  predicted: number;
  ci: number;
  studentScore: number;
  gap: number;
  quota: number;
  competition: number;
  matchCode: string;
  matchPercent: number;
  trend: number[];
  traits: string[];
  tuition: string;
  scholarship: string;
}

const monoFont = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

const tierMeta: Record<
  Tier,
  {
    label: string;
    count: number;
    description: string;
    color: string;
    icon: React.ReactNode;
  }
> = {
  safe: {
    label: "AN TOÀN",
    count: 6,
    description: "Khả năng đỗ cao · Điểm bạn vượt điểm chuẩn",
    color: "#22C55E",
    icon: <ShieldCheck size={16} />,
  },
  balance: {
    label: "CÂN BẰNG",
    count: 11,
    description: "Vừa sức · Cần chiến lược nguyện vọng rõ ràng",
    color: "#F59E0B",
    icon: <Gauge size={16} />,
  },
  challenge: {
    label: "THỬ THÁCH",
    count: 7,
    description: "Đột phá · Dùng như mục tiêu cao nhưng có phương án dự phòng",
    color: "#EF4444",
    icon: <Zap size={16} />,
  },
};

const options: UniversityOption[] = [
  {
    id: "spkt-cntt",
    tier: "safe",
    university: "Đại học Sư phạm Kỹ thuật - ĐH Đà Nẵng",
    shortName: "SPKT Đà Nẵng",
    major: "CNTT",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 25.5,
    ci: 0.6,
    studentScore: 26.1,
    gap: 0.6,
    quota: 120,
    competition: 13.2,
    matchCode: "RI",
    matchPercent: 89,
    trend: [22.8, 23.4, 24.2, 24.8, 25.1, 25.5],
    traits: ["Kỹ thuật", "Phân tích", "Lập trình", "Hệ thống"],
    tuition: "25 triệu / năm",
    scholarship: "Điểm ≥ 27.0 → 50% HV",
  },
  {
    id: "spkt-dien",
    tier: "safe",
    university: "Đại học Sư phạm Kỹ thuật - ĐH Đà Nẵng",
    shortName: "SPKT Đà Nẵng",
    major: "Kỹ thuật điện",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 22.3,
    ci: 0.7,
    studentScore: 26.1,
    gap: 3.8,
    quota: 90,
    competition: 8.4,
    matchCode: "RI",
    matchPercent: 84,
    trend: [20.1, 20.6, 21.4, 21.8, 22.0, 22.3],
    traits: ["Điện tử", "Thao tác", "Logic", "Thiết bị"],
    tuition: "24 triệu / năm",
    scholarship: "Top 10% đầu vào → 30% HV",
  },
  {
    id: "bkdn-cntt",
    tier: "balance",
    university: "Đại học Bách khoa - ĐH Đà Nẵng",
    shortName: "Bách khoa Đà Nẵng",
    major: "CNTT",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 28.1,
    ci: 0.5,
    studentScore: 26.1,
    gap: -2.0,
    quota: 180,
    competition: 18.6,
    matchCode: "RI",
    matchPercent: 92,
    trend: [26.1, 26.9, 27.2, 27.6, 27.9, 28.1],
    traits: ["Thuật toán", "Phân tích", "Hệ thống", "AI"],
    tuition: "29 triệu / năm",
    scholarship: "Điểm ≥ 28.5 → xét học bổng tài năng",
  },
  {
    id: "ued-is",
    tier: "balance",
    university: "Đại học Kinh tế - ĐH Đà Nẵng",
    shortName: "Kinh tế Đà Nẵng",
    major: "Hệ thống thông tin",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 25.8,
    ci: 0.6,
    studentScore: 26.1,
    gap: 0.3,
    quota: 130,
    competition: 11.8,
    matchCode: "IC",
    matchPercent: 78,
    trend: [23.8, 24.4, 24.9, 25.1, 25.5, 25.8],
    traits: ["Dữ liệu", "Quy trình", "Phân tích", "Sản phẩm"],
    tuition: "22 triệu / năm",
    scholarship: "GPA lớp 12 ≥ 8.8 → ưu tiên xét HB",
  },
  {
    id: "hust-cntt",
    tier: "challenge",
    university: "Đại học Bách khoa Hà Nội",
    shortName: "Bách khoa Hà Nội",
    major: "CNTT",
    location: "Hà Nội",
    combo: "A00",
    predicted: 29.2,
    ci: 0.4,
    studentScore: 26.1,
    gap: -3.1,
    quota: 300,
    competition: 24.9,
    matchCode: "RI",
    matchPercent: 94,
    trend: [28.0, 28.4, 28.8, 28.9, 29.0, 29.2],
    traits: ["Nghiên cứu", "Kỹ thuật", "AI", "Hệ thống lớn"],
    tuition: "35 triệu / năm",
    scholarship: "Theo đề án tài năng và hồ sơ học thuật",
  },
  {
    id: "bkdn-se",
    tier: "challenge",
    university: "Đại học Bách khoa - ĐH Đà Nẵng",
    shortName: "Bách khoa ĐN",
    major: "Kỹ thuật phần mềm",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 28.5,
    ci: 0.5,
    studentScore: 26.1,
    gap: -2.4,
    quota: 150,
    competition: 21.1,
    matchCode: "RI",
    matchPercent: 90,
    trend: [26.8, 27.2, 27.8, 28.0, 28.3, 28.5],
    traits: ["Lập trình", "Thiết kế hệ thống", "Kiểm thử", "Logic"],
    tuition: "31 triệu / năm",
    scholarship: "Điểm ≥ 28.0 → phỏng vấn học bổng",
  },
];

const selectedDefault = options[0];

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function formatGap(gap: number) {
  return gap > 0 ? `+${gap.toFixed(1)}` : gap.toFixed(1);
}

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 3)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function SectionIntro({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-7 mx-auto w-[min(1540px,100%)] ">
      <span className="mb-2 inline-flex items-center gap-2 text-lg font-bold text-sketch-red" style={{ fontFamily: "var(--font-heading)" }}>
        {eyebrow}
      </span>
      <h2 className="-rotate-[0.4deg] text-[42px] leading-tight text-sketch-ink">{title}</h2>
      <p className="mt-2 max-w-3xl text-xl text-sketch-muted">{children}</p>
    </div>
  );
}

function MiniRadar({ size = 92 }: { size?: number }) {
  const points = "50,7 86,28 86,72 50,93 14,72 14,28";
  const scorePoints = "50,15 76,34 71,68 50,78 24,66 23,34";

  return (
    <svg
      className="overflow-visible"
      width={size}
      height={size}
      viewBox="0 0 100 100"
      role="img"
      aria-label="Biểu đồ radar RIASEC RI"
    >
      <polygon points={points} fill="rgba(255,243,133,0.16)" stroke="#2d2d2d" strokeWidth="1.5" />
      <polygon points="50,22 73,36 73,64 50,78 27,64 27,36" fill="rgba(255,243,133,0.16)" stroke="#2d2d2d" strokeWidth="1.5" />
      <line x1="50" y1="7" x2="50" y2="93" stroke="rgba(45,45,45,0.18)" strokeWidth="1.2" />
      <line x1="14" y1="28" x2="86" y2="72" stroke="rgba(45,45,45,0.18)" strokeWidth="1.2" />
      <line x1="86" y1="28" x2="14" y2="72" stroke="rgba(45,45,45,0.18)" strokeWidth="1.2" />
      <polygon points={scorePoints} fill="rgba(45,93,161,0.2)" stroke="#2d5da1" strokeWidth="3" />
      {["R", "I", "A", "S", "E", "C"].map((label, index) => {
        const labelPositions = [
          [50, 3],
          [93, 27],
          [93, 77],
          [50, 99],
          [7, 77],
          [7, 27],
        ];
        const [x, y] = labelPositions[index];

        return (
          <text key={label} x={x} y={y} textAnchor="middle" fill="#2d2d2d" fontSize="8" fontWeight="800" style={{ fontFamily: monoFont }}>
            {label}
          </text>
        );
      })}
    </svg>
  );
}

function LogoAvatar({ name, size = 42 }: { name: string; size?: number }) {
  return (
    <div
      className="grid shrink-0 place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow text-sketch-ink shadow-[3px_3px_0_#2d2d2d]"
      style={{ width: size, height: size, fontFamily: "var(--font-heading)" }}
    >
      <span className="text-xs font-bold">{initials(name)}</span>
    </div>
  );
}

function RiasecBadge({ code, percent }: { code: string; percent: number }) {
  return (
    <span
      title="R: Realistic · I: Investigative"
      className="shrink-0 rounded-full border-[2px] border-sketch-ink bg-sketch-yellow px-2.5 py-1 text-xs font-extrabold text-sketch-ink shadow-[2px_2px_0_#2d2d2d]"
      style={{ fontFamily: monoFont }}
    >
      {code} · {percent}%
    </span>
  );
}

function Sparkline({ values, tier }: { values: number[]; tier: Tier }) {
  const width = 92;
  const height = 34;
  const min = Math.min(...values) - 0.2;
  const max = Math.max(...values) + 0.2;
  const points = values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / (max - min)) * height;
      return `${x},${y}`;
    })
    .join(" ");
  const lastY = Number(points.split(" ").at(-1)?.split(",")[1] ?? 0);

  return (
    <svg className="h-[34px] w-[92px] overflow-visible" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Xu hướng điểm chuẩn">
      <polyline points={points} fill="none" stroke={tierMeta[tier].color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={width} cy={lastY} r="2.7" fill={tierMeta[tier].color} />
      <circle cx={width - 4} cy={height - 4} r="3" fill="#ffffff" stroke="#2d2d2d" strokeDasharray="2 2" strokeWidth="1.8" />
    </svg>
  );
}

function ScoreComparisonBar({
  option,
  compact = false,
}: {
  option: Pick<UniversityOption, "predicted" | "studentScore" | "gap" | "ci" | "tier">;
  compact?: boolean;
}) {
  const predictedPercent = Math.min(100, (option.predicted / 30) * 100);
  const studentPercent = Math.min(100, (option.studentScore / 30) * 100);
  const ciStart = Math.max(0, ((option.predicted - option.ci) / 30) * 100);
  const ciWidth = Math.min(100 - ciStart, ((option.ci * 2) / 30) * 100);
  const isAbove = option.gap >= 0;

  return (
    <div className={cn("relative w-full border-[2px] border-sketch-ink bg-[#fffdf0] shadow-[inset_0_0_0_3px_rgba(255,243,133,0.32)]", compact ? "p-3.5 wobbly-alt" : "p-3 wobbly-alt")}>
      <div className="flex justify-between gap-3 text-base font-bold text-sketch-muted">
        <span>Điểm chuẩn dự đoán 2025</span>
        <strong className="text-sm text-sketch-ink" style={{ fontFamily: monoFont }}>
          {option.predicted.toFixed(1)} ± {option.ci.toFixed(1)} điểm
        </strong>
      </div>
      <div className="relative my-2 h-5 overflow-visible rounded-full border-[2px] border-sketch-ink bg-sketch-surface-dim">
        <div
          className="absolute inset-y-[-6px] rounded-full border-[2px] border-dashed border-sketch-ink bg-white/35"
          style={{ left: `${ciStart}%`, width: `${ciWidth}%` }}
        />
        <div
          className="h-full rounded-full border-r-[2px] border-sketch-ink"
          style={{ width: `${predictedPercent}%`, backgroundColor: tierMeta[option.tier].color }}
        />
        <div className="absolute top-[-10px] h-[38px] border-l-[3px] border-sketch-ink" style={{ left: `${studentPercent}%` }}>
          <span className="absolute -left-[7px] -top-[3px] h-[13px] w-[13px] rounded-full border-[2px] border-sketch-ink bg-white" />
        </div>
      </div>
      <div className="flex justify-between gap-3 text-base font-bold">
        <span className="text-sm text-sketch-ink" style={{ fontFamily: monoFont }}>
          ▲ Điểm của bạn: {option.studentScore.toFixed(1)}
        </span>
        <strong className="text-sm" style={{ color: isAbove ? "#22C55E" : "#EF4444", fontFamily: monoFont }}>
          {formatGap(option.gap)}
        </strong>
      </div>
    </div>
  );
}

function UniversityCard({
  option,
  selected,
  onSelect,
}: {
  option: UniversityOption;
  selected?: boolean;
  onSelect?: (option: UniversityOption) => void;
}) {
  const meta = tierMeta[option.tier];

  return (
    <button
      type="button"
      className={cn(
        "relative grid min-w-0 gap-3 overflow-hidden border-[2px] border-sketch-ink bg-sketch-surface py-4 pl-5 pr-4 text-left text-sketch-ink shadow-sketch transition-all duration-150 wobbly hover:-translate-y-0.5 hover:-rotate-[0.3deg] hover:shadow-sketch-md",
        selected && "outline-[3px]",
      )}
      style={{ outlineColor: selected ? meta.color : undefined }}
      onClick={() => onSelect?.(option)}
    >
      <span className="absolute inset-y-0 left-0 w-1.5" style={{ backgroundColor: meta.color }} />
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <LogoAvatar name={option.shortName} />
          <div className="min-w-0">
            <strong className="block max-w-[150px] truncate text-lg font-bold text-sketch-blue">{option.shortName}</strong>
            <span className="mt-1 flex items-center gap-1 text-[15px] font-bold text-sketch-muted">
              <MapPin size={12} /> {option.location}
            </span>
          </div>
        </div>
        <RiasecBadge code={option.matchCode} percent={option.matchPercent} />
      </div>

      <h4 className="m-0 text-2xl leading-tight text-sketch-ink">{option.major}</h4>

      <div className="flex items-center justify-between gap-3">
        <span className="rounded-full border-[2px] border-sketch-ink bg-sketch-surface-dim px-2.5 py-1 text-xs font-extrabold text-sketch-ink" style={{ fontFamily: monoFont }}>
          {option.combo}
        </span>
        <Sparkline values={option.trend} tier={option.tier} />
      </div>

      <ScoreComparisonBar option={option} />

      <div className="flex items-center justify-between gap-3">
        <span className="text-[15px] font-bold text-sketch-muted">{option.quota} chỉ tiêu</span>
        <span className="text-[15px] font-bold text-sketch-muted">{option.competition.toFixed(1)}× tỷ lệ chọi</span>
        <span className="grid h-8 w-8 place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-blue text-white shadow-[2px_2px_0_#2d2d2d]">
          <ArrowRight size={15} />
        </span>
      </div>
    </button>
  );
}

function TierHeader({ tier }: { tier: Tier }) {
  const meta = tierMeta[tier];

  return (
    <div
      className="mb-3 grid grid-cols-[1fr_auto] gap-x-3 gap-y-1 border-[2px] border-l-[8px] border-sketch-ink bg-white p-3.5 shadow-sketch wobbly-alt"
      style={{ borderLeftColor: meta.color, backgroundColor: `${meta.color}1f` }}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="h-3 w-3 rounded-full border-[2px] border-sketch-ink" style={{ backgroundColor: meta.color }} />
        <strong className="text-[22px] leading-none text-sketch-ink">{meta.label}</strong>
        <span className="rounded-full border-[2px] border-sketch-ink bg-white px-2 py-0.5 text-xs font-extrabold text-sketch-ink" style={{ fontFamily: monoFont }}>
          {meta.count} lựa chọn
        </span>
      </div>
      <ChevronDown size={18} className="row-span-2 self-center text-sketch-ink" />
      <p className="m-0 text-[17px] text-[#5f5350]">{meta.description}</p>
    </div>
  );
}

function TierSection({
  tier,
  selectedId,
  onSelect,
}: {
  tier: Tier;
  selectedId: string;
  onSelect: (option: UniversityOption) => void;
}) {
  return (
    <section className="mb-6">
      <TierHeader tier={tier} />
      <div className="grid grid-cols-1 gap-3.5 xl:grid-cols-2">
        {options
          .filter((option) => option.tier === tier)
          .map((option) => (
            <UniversityCard
              key={option.id}
              option={option}
              selected={option.id === selectedId}
              onSelect={onSelect}
            />
          ))}
      </div>
    </section>
  );
}

function DetailGauge({ option }: { option: UniversityOption }) {
  return (
    <div>
      <ScoreComparisonBar option={option} compact />
      <div className="mt-2.5 grid grid-cols-3 gap-2">
        {[
          ["Dự đoán:", option.predicted.toFixed(1)],
          ["Của bạn:", option.studentScore.toFixed(1)],
          ["Chênh:", formatGap(option.gap)],
        ].map(([label, value]) => (
          <span key={label} className="grid gap-1 border-[2px] border-sketch-ink bg-sketch-surface-dim p-2 text-sm font-bold text-sketch-muted wobbly-alt">
            {label}
            <b className="text-sketch-ink" style={{ fontFamily: monoFont }}>{value}</b>
          </span>
        ))}
      </div>
    </div>
  );
}

function HistoricalChart({ option }: { option: UniversityOption }) {
  const values = option.trend;
  const width = 260;
  const height = 118;
  const min = Math.min(...values) - 0.8;
  const max = Math.max(...values) + 0.8;
  const points = values.map((value, index) => {
    const x = 12 + (index / (values.length - 1)) * (width - 24);
    const y = height - 18 - ((value - min) / (max - min)) * (height - 34);
    return [x, y] as const;
  });
  const polyline = points.map(([x, y]) => `${x},${y}`).join(" ");
  const area = `12,${height - 16} ${polyline} ${width - 12},${height - 16}`;

  return (
    <svg className="h-auto w-full border-[2px] border-sketch-ink bg-[#fffdf0] p-2.5 wobbly-alt" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Điểm chuẩn lịch sử 2019 đến 2025">
      <polygon points={area} fill={`${tierMeta[option.tier].color}1f`} />
      <polyline points={polyline} fill="none" stroke={tierMeta[option.tier].color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      {points.map(([x, y], index) => (
        <circle key={`${x}-${y}`} cx={x} cy={y} r={index === points.length - 1 ? 4 : 3} fill="#ffffff" stroke="#2d2d2d" strokeWidth="1.8" />
      ))}
      <line x1={points.at(-2)?.[0]} y1={points.at(-2)?.[1]} x2={points.at(-1)?.[0]} y2={points.at(-1)?.[1]} stroke="#2d2d2d" strokeWidth="1.8" strokeDasharray="4 4" />
      {["2019", "2020", "2021", "2022", "2024", "2025"].map((year, index) => (
        <text key={year} x={12 + (index / 5) * (width - 24)} y={height - 3} fill="#8f6f6d" fontSize="8" fontWeight="700" textAnchor="middle" style={{ fontFamily: monoFont }}>
          {year}
        </text>
      ))}
    </svg>
  );
}

function DetailPanel({ option }: { option: UniversityOption }) {
  const meta = tierMeta[option.tier];

  return (
    <aside className="sticky top-[86px] grid h-[calc(100vh-108px)] grid-rows-[auto_minmax(0,1fr)] self-start overflow-hidden border-[2px] border-sketch-ink bg-sketch-surface shadow-sketch wobbly-alt">
      <header className="sticky top-0 z-10 border-b-[2px] border-sketch-ink bg-sketch-yellow p-4">
        <button type="button" aria-label="Đóng panel" className="absolute right-3 top-3 grid h-[34px] w-[34px] place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-surface text-sketch-ink shadow-[2px_2px_0_#2d2d2d]">
          <X size={17} />
        </button>
        <div className="grid grid-cols-[60px_1fr] items-center gap-3 pr-10">
          <LogoAvatar name={option.shortName} size={60} />
          <div>
            <span className="flex items-center gap-1 text-[15px] font-bold text-sketch-muted">
              <MapPin size={13} /> {option.location}
            </span>
            <h3 className="mt-1 text-[21px] leading-tight text-sketch-ink">{option.university}</h3>
          </div>
        </div>
        <h4 className="my-4 text-[25px] leading-tight text-sketch-blue">{option.major}</h4>
        <span className="inline-flex items-center gap-2 rounded-full border-[2px] border-sketch-ink bg-white px-2.5 py-1 text-[17px] font-bold text-sketch-ink">
          {meta.icon} {meta.label}
        </span>
      </header>

      <div className="overflow-auto bg-sketch-surface p-4">
        <section className="mb-5">
          <h5 className="mb-2.5 text-[22px] text-sketch-red">Phân tích điểm</h5>
          <DetailGauge option={option} />
        </section>

        <section className="mb-5">
          <h5 className="mb-2.5 text-[22px] text-sketch-red">Điểm chuẩn lịch sử (2019-2024)</h5>
          <HistoricalChart option={option} />
        </section>

        <section className="mb-5">
          <h5 className="mb-2.5 text-[22px] text-sketch-red">Độ phù hợp ngành nghề</h5>
          <div className="grid gap-2.5 border-[2px] border-sketch-ink bg-sketch-surface p-3 shadow-[3px_3px_0_#2d2d2d] wobbly-alt">
            <div>
              <strong className="text-[15px] text-sketch-blue" style={{ fontFamily: monoFont }}>
                {option.matchCode} · {option.matchPercent}% phù hợp
              </strong>
              <span className="mt-1 block text-base font-bold text-sketch-muted">
                RIASEC khớp với tín hiệu kỹ thuật và phân tích.
              </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full border-[2px] border-sketch-ink bg-sketch-surface-dim">
              <span className="block h-full border-r-[2px] border-sketch-ink bg-sketch-blue" style={{ width: `${option.matchPercent}%` }} />
            </div>
            <div className="flex flex-wrap gap-2">
              {option.traits.map((trait) => (
                <span key={trait} className="rounded-full border-[2px] border-sketch-ink bg-sketch-yellow px-2 py-1 text-[15px] text-sketch-ink">
                  {trait}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section>
          <h5 className="mb-2.5 text-[22px] text-sketch-red">Thông tin tuyển sinh</h5>
          <div className="grid gap-2">
            <p className="m-0 flex gap-2 border-[2px] border-sketch-ink bg-sketch-bg-alt p-2.5 text-base font-bold text-sketch-ink wobbly-alt">
              <CircleDollarSign size={16} className="shrink-0 text-sketch-blue" /> Học phí: {option.tuition}
            </p>
            <p className="m-0 flex gap-2 border-[2px] border-sketch-ink bg-sketch-bg-alt p-2.5 text-base font-bold text-sketch-ink wobbly-alt">
              <GraduationCap size={16} className="shrink-0 text-sketch-blue" /> Học bổng: {option.scholarship}
            </p>
            <p className="m-0 flex gap-2 border-[2px] border-sketch-ink bg-sketch-bg-alt p-2.5 text-base font-bold text-sketch-ink wobbly-alt">
              <ClipboardList size={16} className="shrink-0 text-sketch-blue" /> Chỉ tiêu 2025: {option.quota} (NV1: 80, HVHB: 40)
            </p>
          </div>
          <button type="button" className="mt-2.5 border-0 bg-transparent p-0 text-[17px] font-bold text-sketch-blue">
            Xem đề án tuyển sinh →
          </button>
        </section>
      </div>
    </aside>
  );
}

function RagChatPanel({ option, onBack }: { option: UniversityOption; onBack: () => void }) {
  return (
    <aside className="grid h-full grid-rows-[auto_minmax(0,1fr)_auto] overflow-hidden bg-sketch-surface">
      <header className="sticky top-0 z-10 grid grid-cols-[36px_1fr] items-center gap-2.5 border-b-[2px] border-sketch-ink bg-sketch-yellow p-4">
        <button type="button" onClick={onBack} aria-label="Quay lại chi tiết trường" className="grid h-9 w-9 place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-surface text-sketch-ink shadow-[2px_2px_0_#2d2d2d]">
          <ArrowLeft size={18} />
        </button>
        <div>
          <h3 className="m-0 text-[23px] leading-tight text-sketch-ink">Hỏi về {option.shortName}</h3>
          <span className="mt-1 inline-flex rounded-full border-[2px] border-sketch-ink bg-sketch-surface px-2 py-1 text-[15px] font-bold text-sketch-blue">
            {option.major} · {option.shortName}
          </span>
        </div>
      </header>

      <div className="flex flex-col gap-3 overflow-auto bg-sketch-surface p-4">
        <div className="flex flex-wrap gap-2">
          {["Học phí chi tiết thế nào?", "Điều kiện xét học bổng?", "Cơ hội việc làm ngành này?"].map((question) => (
            <button key={question} type="button" className="rounded-full border-[2px] border-sketch-ink bg-sketch-yellow px-2.5 py-1.5 text-base font-bold text-sketch-ink">
              {question}
            </button>
          ))}
        </div>

        <div className="grid max-w-[92%] grid-cols-[26px_1fr] gap-2 self-start border-[2px] border-sketch-ink bg-sketch-surface-dim p-3 text-[17px] text-sketch-ink shadow-[3px_3px_0_#2d2d2d] wobbly-alt">
          <span className="grid h-[26px] w-[26px] place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow text-sketch-ink">
            <Bot size={15} />
          </span>
          <div>
            <p className="m-0 leading-snug">
              Với hồ sơ RI và điểm A00 hiện tại, ngành {option.major} tại {option.shortName} là lựa chọn có độ phù hợp cao. Điểm cần chú ý là biên độ dự đoán ±{option.ci.toFixed(1)} điểm, nên bạn vẫn nên đặt thêm một nguyện vọng an toàn phía sau.
            </p>
            <small className="mt-2 block text-sm font-bold text-sketch-muted">📄 Đề án tuyển sinh 2025, trang 12</small>
          </div>
        </div>

        <div className="max-w-[92%] self-end border-[2px] border-sketch-ink bg-sketch-blue p-3 text-[17px] leading-snug text-white shadow-[3px_3px_0_#2d2d2d] wobbly-alt">
          Em có nên đặt ngành này ở NV1 không?
        </div>

        <div className="grid max-w-[92%] grid-cols-[26px_1fr] gap-2 self-start border-[2px] border-sketch-ink bg-sketch-surface-dim p-3 text-[17px] text-sketch-ink shadow-[3px_3px_0_#2d2d2d] wobbly-alt">
          <span className="grid h-[26px] w-[26px] place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow text-sketch-ink">
            <Bot size={15} />
          </span>
          <div>
            <p className="m-0 leading-snug">
              Có thể đặt NV1 nếu đây là ngành ưu tiên nhất của bạn. Hệ thống khuyến nghị kèm một ngành cùng nhóm tại Đà Nẵng ở tier an toàn để giữ xác suất trúng tuyển ổn định.
            </p>
            <small className="mt-2 block text-sm font-bold text-sketch-muted">📄 Quy chế xét tuyển NV1, mục 3.2</small>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-[1fr_42px] gap-2 border-t-[2px] border-sketch-ink bg-sketch-bg-alt p-4">
        <textarea
          rows={2}
          placeholder="Hỏi về học phí, học bổng, tổ hợp xét tuyển..."
          className="max-h-[84px] min-h-11 resize-y border-[2px] border-sketch-ink bg-sketch-surface px-3 py-2.5 text-[17px] text-sketch-ink outline-none wobbly-alt"
        />
        <button type="button" aria-label="Gửi câu hỏi" className="grid h-[42px] w-[42px] place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-blue text-white shadow-[2px_2px_0_#2d2d2d]">
          <SendHorizontal size={18} />
        </button>
        <p className="col-span-2 m-0 text-sm font-bold text-sketch-muted">Câu trả lời dựa trên đề án tuyển sinh chính thức</p>
      </div>
    </aside>
  );
}

function Sidebar() {
  return (
    <aside className="sticky top-[86px] max-h-[calc(100vh-108px)] self-start overflow-auto border-[2px] border-sketch-ink bg-sketch-surface p-4 shadow-sketch -rotate-[0.35deg] wobbly">
      <div className="grid gap-4">
        <div className="flex items-center gap-3">
          <div className="grid h-[50px] w-[50px] place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow text-xl font-bold text-sketch-ink shadow-[3px_3px_0_#2d2d2d]">
            AN
          </div>
          <div>
            <span className="block text-base font-bold text-sketch-muted">Hồ sơ học sinh</span>
            <strong className="mt-0.5 block text-[22px] leading-none text-sketch-blue">Nguyễn Văn An</strong>
          </div>
        </div>

        <div className="border-y-[2px] border-dashed border-sketch-ink/20 py-3.5">
          {[
            ["Tổ hợp A00", "26.1 điểm"],
            ["Học bạ TB", "8.4 / 10"],
            ["Khu vực", "KV2 · +0.5"],
          ].map(([label, value]) => (
            <p key={label} className="mb-2 flex justify-between gap-2 text-[17px] text-sketch-muted last:mb-0">
              <span>{label}</span>
              <b className="text-sm text-sketch-ink" style={{ fontFamily: monoFont }}>{value}</b>
            </p>
          ))}
        </div>

        <div className="grid grid-cols-[104px_1fr] items-center gap-3">
          <MiniRadar size={100} />
          <div>
            <span className="block text-base font-bold text-sketch-muted">RIASEC top</span>
            <div className="mt-2 flex flex-wrap gap-2">
              {[
                ["R", "#34D399"],
                ["I", "#60CFFF"],
              ].map(([label, color]) => (
                <b key={label} className="grid h-8 w-8 place-items-center rounded-full border-[2px] border-sketch-ink text-sketch-ink shadow-[2px_2px_0_#2d2d2d]" style={{ backgroundColor: color, fontFamily: monoFont }}>
                  {label}
                </b>
              ))}
            </div>
            <p className="mt-2 text-[15px] text-sketch-muted">Realistic 72 · Investigative 65</p>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-3.5 border-t-[2px] border-dashed border-sketch-ink/20 pt-4">
        <h3 className="m-0 flex items-center gap-2 text-[22px] text-sketch-red">
          <SlidersHorizontal size={16} /> Lọc kết quả
        </h3>
        <label className="grid gap-2 text-[17px] font-bold text-sketch-ink">
          Tổ hợp môn
          <span className="flex items-center justify-between gap-2 border-[2px] border-sketch-ink bg-sketch-surface px-3 py-2 text-[17px] font-bold text-sketch-ink shadow-[3px_3px_0_#2d2d2d] wobbly-btn">
            A00 <ChevronDown size={14} />
          </span>
        </label>
        <label className="grid gap-2 text-[17px] font-bold text-sketch-ink">
          Khu vực học
          <div className="grid grid-cols-2 gap-2">
            {["Đà Nẵng", "Hà Nội", "HCM", "Tất cả"].map((region, index) => (
              <button
                key={region}
                type="button"
                className={cn(
                  "rounded-full border-[2px] border-sketch-ink px-2 py-1.5 text-[15px] font-bold text-sketch-ink transition-transform hover:-translate-y-0.5",
                  index === 0 ? "bg-sketch-yellow" : "bg-sketch-surface-dim",
                )}
              >
                {region}
              </button>
            ))}
          </div>
        </label>
        <label className="grid gap-2 text-[17px] font-bold text-sketch-ink">
          Khớp RIASEC ≥ <b className="text-sketch-blue" style={{ fontFamily: monoFont }}>70%</b>
          <span className="relative h-2.5 rounded-full border-[2px] border-sketch-ink bg-sketch-surface-dim">
            <i className="absolute inset-y-0 left-0 right-[30%] rounded-full bg-sketch-blue" />
            <i className="absolute left-[70%] top-1/2 h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border-[2px] border-sketch-ink bg-sketch-yellow shadow-[2px_2px_0_#2d2d2d]" />
          </span>
        </label>
      </div>

      <div className="mt-5 border-t-[2px] border-dashed border-sketch-ink/20 pt-3.5">
        <p className="mb-2 flex justify-between text-[17px] text-sketch-muted">
          Tìm thấy <b className="text-sketch-ink" style={{ fontFamily: monoFont }}>24 ngành</b>
        </p>
        <p className="m-0 flex justify-between text-[17px] text-sketch-muted">
          Từ <b className="text-sketch-ink" style={{ fontFamily: monoFont }}>12 trường đại học</b>
        </p>
      </div>
    </aside>
  );
}

function BridgeScreen() {
  return (
    <section id="transition-bridge" className="relative grid min-h-[calc(100vh-70px)] place-items-center overflow-hidden px-7 py-[72px]">
      <div className="absolute inset-0 opacity-55 [background-image:linear-gradient(90deg,rgba(45,45,45,0.05)_1px,transparent_1px),linear-gradient(rgba(45,45,45,0.05)_1px,transparent_1px)] [background-size:40px_40px] -rotate-1 scale-[1.04]" />
      <div className="absolute left-1/2 top-[13%] h-[170px] w-[min(820px,82vw)] -translate-x-1/2 -rotate-2 border-[2px] border-dashed border-sketch-ink/20 bg-[repeating-linear-gradient(-8deg,rgba(255,243,133,0.46)_0_12px,rgba(255,243,133,0.2)_12px_24px)] wobbly" />

      <div className="relative z-10 flex w-[min(960px,100%)] flex-col items-center text-center">
        <div className="inline-flex max-w-full rotate-[0.7deg] items-center gap-3.5 border-[2px] border-sketch-ink bg-sketch-surface py-2 pl-2 pr-4 text-lg font-bold text-sketch-ink shadow-sketch wobbly-btn">
          <MiniRadar size={80} />
          <span>Hồ sơ năng lực: <b className="text-sketch-blue" style={{ fontFamily: monoFont }}>RI</b> · Kỹ thuật + Nghiên cứu</span>
        </div>
        <h1 className="-rotate-[0.8deg] mb-2.5 mt-8 max-w-[860px] text-[64px] leading-none text-sketch-red">
          Tìm trường phù hợp với bạn
        </h1>
        <p className="m-0 text-2xl text-sketch-muted">Dựa trên năng lực và điểm số thực tế</p>

        <div className="my-10 grid w-[min(960px,100%)] grid-cols-1 gap-5 md:grid-cols-3">
          {[
            ["🎯 An toàn — Chắc đỗ", "Điểm của bạn vượt vùng dự đoán, phù hợp để giữ nhịp.", tierMeta.safe.color, "-rotate-[0.4deg]"],
            ["⚖️ Cân bằng — Vừa sức", "Độ cạnh tranh vừa đủ để tối ưu nguyện vọng chính.", tierMeta.balance.color, "rotate-[0.8deg]"],
            ["🚀 Thử thách — Đột phá", "Mục tiêu cao để bạn thử sức mà vẫn có phương án sau.", tierMeta.challenge.color, "-rotate-[0.8deg]"],
          ].map(([title, desc, color, rotate]) => (
            <div
              key={title}
              className={cn("min-h-34 border-[2px] border-l-[8px] border-sketch-ink bg-sketch-surface p-5 text-left shadow-sketch-md transition-transform hover:-translate-y-1 wobbly", rotate)}
              style={{ borderLeftColor: color }}
            >
              <strong className="mb-2 block text-[22px] leading-tight text-sketch-blue">{title}</strong>
              <span className="text-lg text-sketch-muted">{desc}</span>
            </div>
          ))}
        </div>

        <a
          href="#main-results"
          className="inline-flex min-h-[54px] w-[min(360px,100%)] items-center justify-center gap-2 border-[2px] border-sketch-ink bg-sketch-red text-[22px] font-bold text-white shadow-sketch transition-all hover:translate-x-0.5 hover:translate-y-0.5 hover:no-underline hover:shadow-pressed wobbly-btn"
        >
          Xem kết quả của tôi <ArrowRight size={18} />
        </a>
      </div>
    </section>
  );
}

function DashboardScreen() {
  const [selected, setSelected] = useState<UniversityOption>(selectedDefault);
  const groupedCounts = useMemo(() => ({ safe: 6, balance: 11, challenge: 7 }), []);

  return (
    <section id="main-results" className="border-y-[2px] border-sketch-ink bg-sketch-bg-alt px-7 py-15">
      <SectionIntro eyebrow="" title="Gợi ý nhóm ngành và trường phù hợp với bạn">
        Danh sách trường được nhóm theo xác suất, nhưng luôn giải thích bằng điểm số, RIASEC và dữ liệu tuyển sinh.
      </SectionIntro>

      <div className="mx-auto grid min-h-[860px] w-[min(1540px,100%)] grid-cols-1 items-stretch gap-5 lg:grid-cols-2">
        <Sidebar />

        <main className="overflow-hidden border-[2px] border-sketch-ink bg-sketch-surface p-4 shadow-sketch rotate-[0.15deg] wobbly-alt">
          <div className="mb-5 flex flex-col items-start justify-between gap-4 xl:flex-row xl:items-center">
            <div className="flex flex-wrap gap-2">
              {[
                ["Tất cả", ""],
                ["An toàn", `●${groupedCounts.safe}`],
                ["Cân bằng", `●${groupedCounts.balance}`],
                ["Thử thách", `●${groupedCounts.challenge}`],
              ].map(([label, count], index) => (
                <button
                  key={label}
                  type="button"
                  className={cn(
                    "border-[2px] border-sketch-ink px-3.5 py-2 text-[17px] font-bold text-sketch-ink shadow-[3px_3px_0_#2d2d2d] transition-all hover:translate-x-px hover:translate-y-px hover:bg-sketch-yellow hover:shadow-[1px_1px_0_#2d2d2d] wobbly-btn",
                    index === 0 ? "bg-sketch-yellow" : "bg-sketch-surface",
                  )}
                >
                  {label} {count && <span className="text-sm text-sketch-blue" style={{ fontFamily: monoFont }}>{count}</span>}
                </button>
              ))}
            </div>
            <button type="button" className="flex min-w-44 items-center justify-between gap-2 border-[2px] border-sketch-ink bg-sketch-surface px-3 py-2 text-[17px] font-bold text-sketch-ink shadow-[3px_3px_0_#2d2d2d] wobbly-btn">
              <Search size={15} /> Độ phù hợp <ChevronDown size={15} />
            </button>
          </div>

          <TierSection tier="safe" selectedId={selected.id} onSelect={setSelected} />
          <TierSection tier="balance" selectedId={selected.id} onSelect={setSelected} />
          <TierSection tier="challenge" selectedId={selected.id} onSelect={setSelected} />
        </main>
      </div>
    </section>
  );
}

function ChatScreen() {
  return (
    <section id="rag-chat-screen" className="px-7 py-[72px]">
      <SectionIntro eyebrow="Screen 3 · RAG Chat Panel" title="Hỏi đáp theo ngữ cảnh trường">
        Phần chat được tách khỏi dashboard để học sinh hỏi sâu về ngành, trường và cách đặt nguyện vọng.
      </SectionIntro>
      <div className="mx-auto h-[820px] overflow-hidden border-[2px] border-sketch-ink bg-sketch-surface shadow-sketch-md wobbly">
        <RagChatPanel option={selectedDefault} onBack={() => undefined} />
      </div>
    </section>
  );
}

export default function AdmissionPrototype() {
  return (
    <div
      className="min-h-screen bg-sketch-bg text-sketch-ink [background-image:radial-gradient(circle,#e8e4db_1px,transparent_1px)] [background-size:20px_20px]"
      style={{ fontFamily: "var(--font-body)" }}
    >
      <Navbar />

      <DashboardScreen />
      <ChatScreen />

      <button
        type="button"
        className="fixed bottom-5 right-5 z-30 grid h-12 w-12 place-items-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow text-sketch-ink shadow-sketch"
        aria-label="Cuộn lên đầu trang"
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      >
        <ChevronsUp size={18} />
      </button>
    </div>
  );
}
