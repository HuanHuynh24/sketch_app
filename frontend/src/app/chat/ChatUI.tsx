"use client";

import type { KeyboardEvent } from "react";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import {
  AlertTriangle,
  BarChart3,
  Bot,
  Brain,
  CheckCircle2,
  Compass,
  GraduationCap,
  LoaderCircle,
  MessageSquare,
  RefreshCw,
  SendHorizontal,
  Sparkles,
  Trophy,
  User,
} from "lucide-react";
import {
  ApiError,
  DigitalCompetencyProfile,
  RadarAxis,
  RiasecGroup,
  RiasecMessage,
  RiasecMessageType,
  RiasecScore,
  RiasecSession,
  clearAuthSession,
  getAccessToken,
  getMe,
  startRiasecSession,
  submitRiasecAnswer,
} from "@/lib/api";

interface Message {
  id: string;
  role: "ai" | "user";
  text: string;
  type?: RiasecMessageType | "local_error";
  tone?: "normal" | "warning" | "result" | "system";
}

type SubmitStage = "idle" | "sending" | "waiting";

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const fallbackMaxSteps = 7;

const groupColors: Record<RiasecGroup, string> = {
  R: "#ff4d4d",
  I: "#2d5da1",
  A: "#7c3aed",
  S: "#16a34a",
  E: "#ea580c",
  C: "#64748b",
};

const scenarioMessageTypes = new Set<RiasecMessageType>([
  "anchor_scenario",
  "adaptive_scenario",
]);

function makeMessageId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()}`;
}

function getErrorText(err: unknown) {
  if (err instanceof ApiError) {
    if (err.status === 401) {
      return "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
    }

    return err.message;
  }

  return "Không thể kết nối tới hệ thống. Vui lòng kiểm tra backend và thử lại.";
}

function assistantMessagesToLocal(messages: RiasecMessage[] | undefined) {
  return (messages ?? []).map<Message>((message) => ({
    id: message.message_id,
    role: "ai",
    text: message.content,
    type: message.message_type,
    tone:
      message.message_type === "answer_warning"
        ? "warning"
        : message.message_type === "final_result"
          ? "result"
          : ["intro", "question_lead_in", "transition", "completion_lead_in", "answer_reflection"].includes(message.message_type)
            ? "system"
            : "normal",
  }));
}

function getAssistantResponseMessages(data: {
  assistant_messages?: RiasecMessage[];
  assistant_message?: RiasecMessage | null;
}) {
  if (data.assistant_messages && data.assistant_messages.length > 0) {
    return assistantMessagesToLocal(data.assistant_messages);
  }

  return data.assistant_message
    ? assistantMessagesToLocal([data.assistant_message])
    : [];
}

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

function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
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
      label: axis?.label ?? group,
      value: axis?.normalized_score ?? 0,
      rawScore: axis?.score ?? 0,
      confidence: axis?.confidence ?? 0,
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
    <svg viewBox="0 0 360 360" className="w-full max-w-[360px] aspect-square" role="img" aria-label="Biểu đồ radar RIASEC">
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

        return (
          <g key={axis.group}>
            <circle cx={point.x} cy={point.y} r="6" fill={groupColors[axis.group]} stroke="#2d2d2d" strokeWidth="2" />
            <title>
              {axis.label}: {axis.rawScore.toFixed(1)} điểm, tin cậy {Math.round(axis.confidence * 100)}%
            </title>
          </g>
        );
      })}
    </svg>
  );
}

function ResultPanel({ profile }: { profile: DigitalCompetencyProfile }) {
  const axes = profile.radar_chart?.axes ?? [];
  const dominantGroups = profile.dominant_groups ?? [];
  const groupAnalysis = profile.group_analysis ?? [];
  const recommendations = profile.career_recommendations;

  return (
    <section className="self-stretch border-[2px] border-sketch-ink bg-sketch-yellow wobbly shadow-sketch-md p-5 md:p-6">
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 border-[2px] border-sketch-ink bg-sketch-surface rounded-full font-bold text-sketch-blue">
            <Trophy size={18} /> Mã RIASEC
          </div>
          <h3 className="mt-3 text-sketch-red" style={{ fontSize: 32 }}>
            {profile.riasec_code}
          </h3>
          <p className="max-w-3xl text-sketch-ink">{profile.summary}</p>
        </div>

        <Link
          href={`/profile?dcp_id=${profile.dcp_id}`}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 border-[2px] border-sketch-ink bg-sketch-surface wobbly-btn shadow-sketch text-sketch-blue font-bold"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          <Compass size={16} /> Xem hồ sơ đầy đủ
        </Link>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[420px_1fr] gap-5">
        <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 font-bold text-sketch-blue">
            <BarChart3 size={18} /> Radar RIASEC
          </div>
          <div className="flex justify-center">
            <RiasecRadar axes={axes} />
          </div>
          <ScoreBars scores={profile.scores} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
            <h4 className="text-sketch-blue mb-3 flex items-center gap-2" style={{ fontSize: 21 }}>
              <Sparkles size={18} /> Nhóm nổi bật
            </h4>
            <div className="space-y-3">
              {dominantGroups.map((group) => (
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
            <h4 className="text-sketch-blue mb-3 flex items-center gap-2" style={{ fontSize: 21 }}>
              <GraduationCap size={18} /> Ngành phù hợp
            </h4>
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
            <h4 className="text-sketch-blue mb-3 flex items-center gap-2" style={{ fontSize: 21 }}>
              <Brain size={18} /> Phân tích chi tiết
            </h4>
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

function SubmitStatus({ stage }: { stage: SubmitStage }) {
  if (stage === "idle") {
    return null;
  }

  const isSending = stage === "sending";

  return (
    <div
      role="status"
      aria-live="polite"
      className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-ink bg-sketch-surface shadow-sketch rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
    >
      <div className="flex items-center gap-2 font-bold text-sketch-blue" style={{ fontFamily: "var(--font-heading)" }}>
        <LoaderCircle size={18} className="animate-spin" />
        {isSending ? "Đang gửi câu trả lời..." : "Đang chờ phản hồi..."}
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 text-sm font-bold" style={{ fontFamily: "var(--font-heading)" }}>
        <div className={`flex items-center justify-center gap-1 border-[2px] border-sketch-ink px-3 py-2 ${isSending ? "bg-sketch-yellow text-sketch-ink" : "bg-sketch-blue text-white"}`}>
          <SendHorizontal size={14} /> Gửi
        </div>
        <div className={`flex items-center justify-center gap-1 border-[2px] border-sketch-ink px-3 py-2 ${isSending ? "bg-sketch-bg text-sketch-muted" : "bg-sketch-yellow text-sketch-ink"}`}>
          <Bot size={14} /> Phản hồi
        </div>
      </div>
    </div>
  );
}

export default function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [session, setSession] = useState<RiasecSession | null>(null);
  const [profile, setProfile] = useState<DigitalCompetencyProfile | null>(null);
  const [dcpId, setDcpId] = useState<string | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [warning, setWarning] = useState("");
  const [error, setError] = useState("");
  const [authError, setAuthError] = useState("");
  const [isLoadingSession, setIsLoadingSession] = useState(true);
  const [submitStage, setSubmitStage] = useState<SubmitStage>("idle");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const isSubmitting = submitStage !== "idle";
  const maxSteps = session?.max_steps ?? fallbackMaxSteps;
  const answeredSteps = session?.current_step ?? 0;
  const progressPercent = Math.round((answeredSteps / maxSteps) * 100);
  const displayStep = session
    ? Math.min(session.status === "completed" ? session.current_step : session.current_step + 1, maxSteps)
    : 1;
  const isCompleted = session?.status === "completed";
  const isInputDisabled = isLoadingSession || isSubmitting || Boolean(authError) || !session || isCompleted;

  const verifyCurrentStudent = async () => {
    if (!getAccessToken()) {
      throw new ApiError("Bạn cần đăng nhập trước khi bắt đầu hội thoại.", 401, null);
    }

    await getMe();
  };

  const startConversation = async () => {
    setIsLoadingSession(true);
    setSubmitStage("idle");
    setWarning("");
    setError("");
    setAuthError("");
    setProfile(null);
    setDcpId(null);
    setIsLoadingProfile(false);
    setSession(null);
    setMessages([]);

    try {
      await verifyCurrentStudent();
      const data = await startRiasecSession();

      setSession(data.session);
      setMessages(
        data.assistant_messages?.length
          ? assistantMessagesToLocal(data.assistant_messages)
          : assistantMessagesToLocal([data.question]),
      );
    } catch (err) {
      if (err instanceof ApiError && [400, 401, 404].includes(err.status)) {
        clearAuthSession();
        setAuthError(
          err.status === 401
            ? "Phiên đăng nhập đã hết hạn hoặc chưa tồn tại. Vui lòng đăng nhập lại."
            : "Không tìm thấy thông tin học sinh. Vui lòng đăng nhập lại.",
        );
      } else {
        setError(getErrorText(err));
      }
    } finally {
      setIsLoadingSession(false);
    }
  };

  useEffect(() => {
    void startConversation();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [messages, profile, warning, submitStage]);

  const handleSend = async () => {
    const answerText = input.trim();

    if (!answerText || !session || isInputDisabled || session.status === "completed") {
      return;
    }

    const userMessage: Message = {
      id: makeMessageId(),
      role: "user",
      text: answerText,
      type: "answer",
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setWarning("");
    setError("");
    setSubmitStage("sending");

    let waitingTimer: ReturnType<typeof setTimeout> | undefined;

    try {
      const answerRequest = submitRiasecAnswer(session.session_id, answerText);

      waitingTimer = setTimeout(() => {
        setSubmitStage((currentStage) =>
          currentStage === "sending" ? "waiting" : currentStage,
        );
      }, 300);

      const data = await answerRequest;
      const assistantMessages = getAssistantResponseMessages(data);

      setSession(data.session);
      setMessages((prev) => [...prev, ...assistantMessages]);

      if (data.assistant_message?.message_type === "answer_warning") {
        setWarning(data.assistant_message.content);
        setInput(answerText);
        return;
      }

      if (data.status === "completed") {
        if (data.dcp_id) {
          setDcpId(data.dcp_id);
          setIsLoadingProfile(true);
          try {
            const dcpProfile = await getRiasecProfile(data.dcp_id);
            setProfile(dcpProfile);
          } catch {
            // Fetch thất bại — user vẫn có thể vào profile thủ công
          } finally {
            setIsLoadingProfile(false);
          }
        } else {
          setError("Bài đánh giá đã hoàn tất nhưng backend chưa trả về mã kết quả.");
        }
      }
    } catch (err) {
      const message = getErrorText(err);
      setError(message);
      setInput(answerText);
      setMessages((prev) => [
        ...prev,
        {
          id: makeMessageId(),
          role: "ai",
          text: message,
          type: "local_error",
          tone: "warning",
        },
      ]);
    } finally {
      if (waitingTimer) {
        clearTimeout(waitingTimer);
      }

      setSubmitStage("idle");
    }
  };

  const submitButtonLabel =
    submitStage === "sending"
      ? "Đang gửi..."
      : submitStage === "waiting"
        ? "Chờ phản hồi..."
        : "Gửi";

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Navbar />

      <header
        id="chat-header"
        className="px-5 md:px-8 py-4 border-b-[3px] border-sketch-ink bg-sketch-bg"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-3">
            <MessageSquare size={24} className="text-sketch-red" />
            <div>
              <h2 className="text-sketch-red m-0" style={{ fontFamily: "var(--font-heading)", fontSize: 24 }}>
                Hội thoại RIASEC
              </h2>
              <p className="text-sm text-sketch-muted">Trả lời theo cách bạn thật sự sẽ xử lý tình huống.</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="min-w-[220px]">
              <div className="flex justify-between text-sm font-bold text-sketch-muted mb-1">
                <span>{isLoadingSession ? "Đang khởi tạo..." : session ? `Câu ${displayStep}/${maxSteps}` : "Chưa có phiên"}</span>
                <span>{progressPercent}%</span>
              </div>
              <div className="h-3 border-[2px] border-sketch-ink bg-sketch-surface rounded-full overflow-hidden">
                <div className="h-full bg-sketch-red transition-all" style={{ width: `${progressPercent}%` }} />
              </div>
            </div>

            <button
              type="button"
              onClick={() => void startConversation()}
              disabled={isLoadingSession}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-bold border-[2px] border-sketch-ink bg-sketch-surface wobbly-btn shadow-sketch cursor-pointer disabled:cursor-not-allowed disabled:opacity-60"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              <RefreshCw size={15} /> Làm lại
            </button>
          </div>
        </div>
      </header>

      <main id="chat-messages" className="flex-1 overflow-y-auto px-5 md:px-8 py-6 flex flex-col gap-5">
        {isLoadingSession && (
          <div className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-ink bg-sketch-surface shadow-sketch rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl">
            <div className="flex items-center gap-2 font-bold text-sketch-blue" style={{ fontFamily: "var(--font-heading)" }}>
              <LoaderCircle size={18} className="animate-spin" /> Đang tạo phiên hội thoại...
            </div>
          </div>
        )}

        {authError && (
          <div className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-error bg-red-50 shadow-sketch rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl">
            <div className="flex items-center gap-2 font-bold text-sketch-error mb-2" style={{ fontFamily: "var(--font-heading)" }}>
              <AlertTriangle size={18} /> Cần đăng nhập
            </div>
            <p className="mb-3">{authError}</p>
            <div className="flex flex-wrap gap-3">
              <Link href="/login" className="inline-flex items-center px-4 py-2 border-[2px] border-sketch-ink bg-sketch-red text-white wobbly-btn shadow-sketch">
                Đăng nhập
              </Link>
              <Link href="/signup" className="inline-flex items-center px-4 py-2 border-[2px] border-sketch-ink bg-sketch-yellow text-sketch-ink wobbly-btn shadow-sketch">
                Tạo tài khoản
              </Link>
            </div>
          </div>
        )}

        {error && !authError && (
          <div className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-error bg-red-50 shadow-sketch rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl">
            <div className="flex items-center gap-2 font-bold text-sketch-error" style={{ fontFamily: "var(--font-heading)" }}>
              <AlertTriangle size={18} /> {error}
            </div>
          </div>
        )}

        {messages.map((msg) => {
          const isUser = msg.role === "user";
          const isSystem = msg.tone === "system";
          const isScenario = Boolean(msg.type && scenarioMessageTypes.has(msg.type as RiasecMessageType));
          const label = isUser ? "Bạn" : "SketchAI";

          return (
            <article
              key={msg.id}
              id={`chat-msg-${msg.id}`}
              className={`max-w-[94%] md:max-w-[74%] px-5 py-4 border-[2px] border-sketch-ink text-lg leading-relaxed ${
                isUser
                  ? "self-end bg-sketch-blue text-white shadow-sketch-blue rotate-[0.5deg] rounded-tl-2xl rounded-tr-sm rounded-br-2xl rounded-bl-2xl"
                  : msg.tone === "warning"
                    ? "self-start bg-red-50 shadow-sketch -rotate-[0.5deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
                    : msg.tone === "result"
                      ? "self-start bg-sketch-yellow shadow-sketch-md -rotate-[0.5deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
                      : isSystem
                        ? "self-start bg-sketch-bg-alt shadow-sketch -rotate-[0.25deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
                        : "self-start bg-sketch-surface shadow-sketch -rotate-[0.5deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
              }`}
            >
              <div className="flex items-center justify-between gap-3 mb-2">
                <div
                  className={`flex items-center gap-1 text-sm font-bold opacity-75 ${isUser ? "text-white" : "text-sketch-ink"}`}
                  style={{ fontFamily: "var(--font-heading)" }}
                >
                  {isUser ? <User size={14} /> : isSystem ? <CheckCircle2 size={14} /> : <Bot size={14} />}
                  {label}
                </div>

                {isScenario && (
                  <span
                    className="inline-flex items-center gap-1 px-2 py-0.5 border-[2px] border-sketch-ink bg-sketch-yellow rounded-full text-xs font-bold text-sketch-ink"
                    style={{ fontFamily: "var(--font-heading)" }}
                  >
                    <MessageSquare size={12} /> Câu hỏi tình huống
                  </span>
                )}
              </div>
              <p style={{ whiteSpace: "pre-line" }}>{msg.text}</p>
            </article>
          );
        })}

        <SubmitStatus stage={submitStage} />

        {warning && (
          <p role="status" className="self-start text-sm font-bold text-sketch-error">
            {warning}
          </p>
        )}

        {isLoadingProfile && (
          <div className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-ink bg-sketch-yellow shadow-sketch-md rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl">
            <div className="flex items-center gap-2 font-bold text-sketch-ink" style={{ fontFamily: "var(--font-heading)" }}>
              <LoaderCircle size={18} className="animate-spin" />
              Đang tổng hợp kết quả RIASEC của bạn...
            </div>
            <p className="text-sm text-sketch-muted mt-1">Vui lòng chờ trong giây lát, AI đang phân tích hồ sơ.</p>
          </div>
        )}

        {!isLoadingProfile && profile && <ResultPanel profile={profile} />}

        {!isLoadingProfile && !profile && dcpId && (
          <div className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-error bg-red-50 shadow-sketch rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl">
            <div className="flex items-center gap-2 font-bold text-sketch-error mb-2" style={{ fontFamily: "var(--font-heading)" }}>
              <AlertTriangle size={18} /> Không thể tải kết quả tự động
            </div>
            <p className="text-sm mb-3">Bài đánh giá đã hoàn tất. Nhấn bên dưới để xem kết quả đầy đủ.</p>
            <Link
              href={`/profile?dcp_id=${dcpId}`}
              className="inline-flex items-center gap-2 px-4 py-2 border-[2px] border-sketch-ink bg-sketch-blue text-white wobbly-btn shadow-sketch font-bold"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              <Compass size={16} /> Xem kết quả RIASEC
            </Link>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <footer
        id="chat-input-bar"
        className="flex flex-col md:flex-row gap-4 px-5 md:px-8 py-4 border-t-[3px] border-sketch-ink bg-sketch-bg"
      >
        <input
          id="chat-input"
          type="text"
          placeholder={isCompleted ? "Bài đánh giá đã hoàn tất." : "Nhập câu trả lời của bạn..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isInputDisabled}
          className="flex-1 px-5 py-3 border-[2px] border-sketch-ink wobbly-alt bg-sketch-surface text-lg outline-none focus:border-sketch-blue focus:shadow-sketch-blue transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-60"
          style={{ fontFamily: "var(--font-body)" }}
        />
        <button
          type="button"
          onClick={() => void handleSend()}
          disabled={isInputDisabled || !input.trim()}
          id="chat-send-btn"
          className="inline-flex items-center justify-center gap-2 px-6 py-3 text-white font-bold border-[2px] border-sketch-ink bg-sketch-red wobbly-btn shadow-sketch text-lg cursor-pointer transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1 disabled:cursor-not-allowed disabled:opacity-60"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          {isSubmitting ? <LoaderCircle size={18} className="animate-spin" /> : <SendHorizontal size={18} />}
          {submitButtonLabel}
        </button>
      </footer>
    </div>
  );
}
