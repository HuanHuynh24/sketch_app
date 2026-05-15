"use client";

import type { KeyboardEvent } from "react";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import {
  AlertTriangle,
  BarChart3,
  Bot,
  LoaderCircle,
  MessageSquare,
  RefreshCw,
  SendHorizontal,
  Trophy,
  User,
} from "lucide-react";
import {
  ApiError,
  DigitalCompetencyProfile,
  RiasecGroup,
  RiasecScore,
  RiasecSession,
  clearAuthSession,
  getAccessToken,
  getMe,
  getRiasecProfile,
  getStudentId,
  saveStudentId,
  startRiasecSession,
  submitRiasecAnswer,
} from "@/lib/api";

interface Message {
  id: string;
  role: "ai" | "user";
  text: string;
  tone?: "normal" | "warning" | "result";
}

const riasecGroups: RiasecGroup[] = ["R", "I", "A", "S", "E", "C"];
const fallbackMaxSteps = 7;

function makeMessageId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()}`;
}

function getErrorText(err: unknown) {
  if (err instanceof ApiError) {
    if (err.status === 404 || err.status === 400) {
      return "Không tìm thấy thông tin học sinh. Vui lòng đăng nhập lại.";
    }

    return err.message;
  }

  return "Không thể kết nối tới hệ thống. Vui lòng kiểm tra backend và thử lại.";
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
              className="w-7 h-7 inline-flex items-center justify-center rounded-full border-[2px] border-sketch-ink bg-sketch-yellow font-bold"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {group}
            </span>
            <div className="flex-1 h-4 border-[2px] border-sketch-ink rounded-full overflow-hidden bg-sketch-surface">
              <div className="h-full bg-sketch-blue" style={{ width }} />
            </div>
            <span className="min-w-10 text-right text-sm font-bold">{value.toFixed(1)}</span>
          </div>
        );
      })}
    </div>
  );
}

function ResultPanel({ profile }: { profile: DigitalCompetencyProfile }) {
  return (
    <div className="self-stretch border-[2px] border-sketch-ink bg-sketch-yellow wobbly shadow-sketch p-5">
      <div className="flex items-center gap-2 mb-3 text-sketch-red">
        <Trophy size={22} />
        <h3 className="m-0" style={{ fontSize: 24 }}>
          Kết quả RIASEC: {profile.riasec_code}
        </h3>
      </div>

      <p className="mb-4 text-sketch-ink">{profile.summary}</p>

      <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 mb-3 font-bold text-sketch-blue">
          <BarChart3 size={18} /> Điểm RIASEC
        </div>
        <ScoreBars scores={profile.scores} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
          <h4 className="text-sketch-blue mb-2" style={{ fontSize: 19 }}>
            Nhóm ngành phù hợp
          </h4>
          <p>{profile.career_groups.join(", ") || "Chưa có dữ liệu."}</p>
        </div>

        <div className="bg-sketch-surface border-[2px] border-sketch-ink rounded-lg p-4">
          <h4 className="text-sketch-blue mb-2" style={{ fontSize: 19 }}>
            Ngành học gợi ý
          </h4>
          <p>{profile.recommended_majors.join(", ") || "Chưa có dữ liệu."}</p>
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
  const [warning, setWarning] = useState("");
  const [error, setError] = useState("");
  const [authError, setAuthError] = useState("");
  const [isLoadingSession, setIsLoadingSession] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const maxSteps = session?.max_steps ?? fallbackMaxSteps;
  const displayStep = session
    ? Math.min(session.status === "completed" ? session.current_step : session.current_step + 1, maxSteps)
    : 1;
  const isCompleted = session?.status === "completed";
  const isInputDisabled = isLoadingSession || isSubmitting || Boolean(authError) || !session || isCompleted;

  const resolveStudentId = async () => {
    const storedStudentId = getStudentId();

    if (storedStudentId) {
      return storedStudentId;
    }

    if (!getAccessToken()) {
      throw new ApiError("Bạn cần đăng nhập trước khi bắt đầu hội thoại.", 401, null);
    }

    const me = await getMe();
    saveStudentId(me.student_id);
    return me.student_id;
  };

  const startConversation = async () => {
    setIsLoadingSession(true);
    setIsSubmitting(false);
    setWarning("");
    setError("");
    setAuthError("");
    setProfile(null);
    setSession(null);
    setMessages([]);

    try {
      const studentId = await resolveStudentId();
      const data = await startRiasecSession(studentId);

      setSession(data.session);
      setMessages([
        {
          id: data.question.message_id,
          role: "ai",
          text: data.question.content,
        },
      ]);
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
  }, [messages, profile, warning]);

  const handleSend = async () => {
    const answerText = input.trim();

    if (!answerText || !session || isInputDisabled) {
      return;
    }

    const userMessage: Message = {
      id: makeMessageId(),
      role: "user",
      text: answerText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setWarning("");
    setError("");
    setIsSubmitting(true);

    try {
      const data = await submitRiasecAnswer(session.session_id, answerText);
      setSession(data.session);
      const assistantMessage = data.assistant_message;

      if (assistantMessage?.message_type === "answer_warning") {
        setWarning(assistantMessage.content);
        setInput(answerText);
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessage.message_id,
            role: "ai",
            text: assistantMessage.content,
            tone: "warning",
          },
        ]);
        return;
      }

      if (assistantMessage) {
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessage.message_id,
            role: "ai",
            text: assistantMessage.content,
            tone: data.status === "completed" ? "result" : "normal",
          },
        ]);
      }

      if (data.status === "completed") {
        if (data.dcp_id) {
          const result = await getRiasecProfile(data.dcp_id);
          setProfile(result);
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
          tone: "warning",
        },
      ]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Navbar />

      <div
        id="chat-header"
        className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 px-8 py-4 border-b-[3px] border-sketch-ink bg-sketch-bg"
      >
        <div className="flex items-center gap-3">
          <MessageSquare size={22} className="text-sketch-red" />
          <h2 className="text-sketch-red m-0" style={{ fontFamily: "var(--font-heading)", fontSize: 22 }}>
            Hội thoại RIASEC
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm font-bold text-sketch-muted">
            {isLoadingSession ? "Đang khởi tạo..." : session ? `Câu ${displayStep}/${maxSteps}` : "Chưa có phiên"}
          </span>
          <button
            type="button"
            onClick={() => void startConversation()}
            disabled={isLoadingSession}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-bold border-[2px] border-sketch-ink bg-sketch-surface wobbly-btn shadow-sketch cursor-pointer disabled:cursor-not-allowed disabled:opacity-60"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            <RefreshCw size={15} /> Làm lại
          </button>
        </div>
      </div>

      <div id="chat-messages" className="flex-1 overflow-y-auto px-5 md:px-8 py-6 flex flex-col gap-5">
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
            <Link href="/login" className="text-sketch-blue">
              Đi tới đăng nhập
            </Link>
          </div>
        )}

        {error && !authError && (
          <div className="self-start max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-error bg-red-50 shadow-sketch rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl">
            <div className="flex items-center gap-2 font-bold text-sketch-error" style={{ fontFamily: "var(--font-heading)" }}>
              <AlertTriangle size={18} /> {error}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            id={`chat-msg-${msg.id}`}
            className={`max-w-[90%] md:max-w-[70%] px-5 py-4 border-[2px] border-sketch-ink text-lg leading-relaxed ${
              msg.role === "ai"
                ? msg.tone === "warning"
                  ? "self-start bg-red-50 shadow-sketch -rotate-[0.5deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
                  : "self-start bg-sketch-surface shadow-sketch -rotate-[0.5deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
                : "self-end bg-sketch-blue text-white shadow-sketch-blue rotate-[0.5deg] rounded-tl-2xl rounded-tr-sm rounded-br-2xl rounded-bl-2xl"
            }`}
          >
            <div
              className={`flex items-center gap-1 text-sm font-bold mb-1 opacity-70 ${msg.role === "ai" ? "text-sketch-ink" : "text-white"}`}
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {msg.role === "ai" ? (
                <>
                  <Bot size={14} /> SketchAI
                </>
              ) : (
                <>
                  <User size={14} /> Bạn
                </>
              )}
            </div>
            <p style={{ whiteSpace: "pre-line" }}>{msg.text}</p>
          </div>
        ))}

        {warning && (
          <p role="status" className="self-start text-sm font-bold text-sketch-error">
            {warning}
          </p>
        )}

        {profile && <ResultPanel profile={profile} />}

        <div ref={bottomRef} />
      </div>

      <div
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
          <SendHorizontal size={18} /> {isSubmitting ? "Đang gửi..." : "Gửi"}
        </button>
      </div>
    </div>
  );
}
