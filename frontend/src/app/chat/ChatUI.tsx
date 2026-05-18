

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
  Zap,
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
  getRiasecProfile,
  startRiasecSession,
  submitRiasecAnswer,
} from "@/lib/api";
import { ScoreBars } from './components/ScoreBars';
import { RiasecRadar } from './components/RiasecRadar';
import { ResultPanel } from './components/ResultPanel';
import { SubmitStatus } from './components/SubmitStatus';

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
  R: "#f43f5e", // Rose
  I: "#06b6d4", // Cyan
  A: "#c084fc", // Purple
  S: "#10b981", // Emerald
  E: "#f59e0b", // Amber
  C: "#94a3b8", // Slate
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
            ? "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."
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
    // Add a slight delay for smooth scrolling after DOM updates
    setTimeout(() => {
      bottomRef.current?.scrollIntoView({ block: "end", behavior: "smooth" });
    }, 100);
  }, [messages, profile, warning, submitStage, isLoadingProfile]);

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
      }, 400);

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
            // Fetch thất bại
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
      if (waitingTimer) clearTimeout(waitingTimer);
      setSubmitStage("idle");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#030014] text-white relative overflow-hidden">
      
      {/* Immersive Background */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_0%,rgba(124,58,237,0.1),transparent_50%)]"></div>
        <div className="absolute bottom-0 right-0 w-full h-full bg-[radial-gradient(circle_at_100%_100%,rgba(6,182,212,0.05),transparent_50%)]"></div>
        <div className="absolute w-[800px] h-[800px] bg-[#7c3aed] opacity-5 blur-[150px] rounded-full top-[20%] left-[-20%] animate-pulse-glow" style={{ animationDuration: '8s' }}></div>
      </div>
      
      <div className="relative z-50">
        <Navbar />
      </div>

      {/* Cyberpunk HUD Header */}
      <header className="px-5 md:px-8 py-4 border-b border-white/5 bg-black/40 backdrop-blur-xl relative z-40 shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#06b6d4] to-[#7c3aed] p-[1px] shadow-[0_0_20px_rgba(6,182,212,0.3)]">
               <div className="w-full h-full bg-[#030014] rounded-[15px] flex items-center justify-center relative overflow-hidden">
                 <div className="absolute inset-0 bg-[#06b6d4] opacity-20 animate-pulse"></div>
                 <Brain size={24} className="text-[#06b6d4] relative z-10" />
               </div>
            </div>
            <div>
              <h2 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-[#94a3b8] tracking-tight uppercase">
                Hệ thống Khảo sát
              </h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]"></span>
                <span className="text-xs text-[#06b6d4] font-mono tracking-widest">AI NEURAL NETWORK ACTIVE</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2 min-w-[250px]">
            <div className="flex justify-between text-xs font-bold text-[#94a3b8] uppercase tracking-[0.2em]">
              <span>TIẾN ĐỘ THU THẬP ({isLoadingSession ? "..." : session ? `${displayStep}/${maxSteps}` : "0"})</span>
              <span className="text-[#06b6d4] font-mono">{progressPercent}%</span>
            </div>
            <div className="h-1.5 bg-black rounded-full overflow-hidden border border-white/10 shadow-inner">
              <div 
                className="h-full bg-gradient-to-r from-[#7c3aed] via-[#06b6d4] to-white shadow-[0_0_15px_#06b6d4] transition-all duration-1000 ease-out relative" 
                style={{ width: `${progressPercent}%` }} 
              >
                <div className="absolute top-0 right-0 w-8 h-full bg-white opacity-50 blur-[2px]"></div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main id="chat-messages" className="flex-1 overflow-y-auto px-5 md:px-8 py-10 flex flex-col gap-8 relative z-10 scroll-smooth custom-scrollbar">
        <style>{`
          .custom-scrollbar::-webkit-scrollbar { width: 6px; }
          .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
          .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
        `}</style>
        
        <div className="max-w-4xl w-full mx-auto flex flex-col gap-8">
          
          {isLoadingSession && (
            <div className="self-center flex flex-col items-center gap-4 mt-20 opacity-0 animate-[slideUp_0.5s_ease-out_forwards]">
              <div className="w-20 h-20 rounded-full bg-transparent border-[3px] border-[#06b6d4]/30 border-t-[#06b6d4] animate-spin flex items-center justify-center shadow-[0_0_30px_rgba(6,182,212,0.2)]">
                <div className="w-12 h-12 rounded-full border-[3px] border-[#7c3aed]/30 border-b-[#7c3aed] animate-[spin_1.5s_linear_infinite_reverse]"></div>
              </div>
              <div className="text-lg font-mono text-[#06b6d4] tracking-widest uppercase mt-4">
                Đang thiết lập chuỗi hội thoại...
              </div>
            </div>
          )}

          {authError && (
            <div className="self-center w-full max-w-lg mt-10 glass-panel border border-[#f43f5e]/50 bg-[#f43f5e]/10 p-10 text-center rounded-[2rem] shadow-[0_20px_50px_rgba(244,63,94,0.2)]">
              <div className="w-20 h-20 rounded-2xl bg-[#f43f5e]/20 flex items-center justify-center mx-auto mb-6 text-[#f43f5e] border border-[#f43f5e]/30 shadow-inner">
                <AlertTriangle size={32} />
              </div>
              <h3 className="text-3xl font-bold text-white mb-3 tracking-tight">Hết phiên đăng nhập</h3>
              <p className="text-[#94a3b8] mb-8 text-lg">{authError}</p>
              <div className="flex justify-center gap-4">
                <Link href="/login" className="btn-premium px-8 py-3 text-lg w-full">Đăng nhập ngay</Link>
              </div>
            </div>
          )}

          {error && !authError && (
            <div className="self-center glass-panel border border-[#f43f5e]/50 bg-[#f43f5e]/10 px-6 py-4 rounded-2xl flex items-center gap-4 text-base text-[#f43f5e] shadow-[0_10px_30px_rgba(244,63,94,0.2)]">
              <AlertTriangle size={20} className="shrink-0" /> <span className="font-medium">{error}</span>
            </div>
          )}

          {messages.map((msg, idx) => {
            const isUser = msg.role === "user";
            const isSystem = msg.tone === "system";
            const isScenario = Boolean(msg.type && scenarioMessageTypes.has(msg.type as RiasecMessageType));
            const isResult = msg.tone === "result";

            // Animation for new messages
            const isLatest = idx === messages.length - 1;
            const animationClass = isLatest ? "animate-[slideUp_0.5s_ease-out_forwards]" : "";

            return (
              <div key={msg.id} className={`flex w-full ${isUser ? "justify-end" : "justify-start"} ${animationClass}`}>
                <div className={`flex gap-4 max-w-[90%] md:max-w-[80%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
                  
                  {/* Avatar */}
                  <div className="shrink-0 pt-2">
                    {isUser ? (
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#c084fc] to-[#7c3aed] flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.4)] border border-white/20">
                        <User size={18} className="text-white" />
                      </div>
                    ) : (
                      <div className={`w-10 h-10 rounded-2xl border flex items-center justify-center relative overflow-hidden ${isSystem ? 'bg-black/50 border-white/10' : 'bg-[#030014] border-[#06b6d4]/50 shadow-[0_0_20px_rgba(6,182,212,0.4)]'}`}>
                        {!isSystem && <div className="absolute inset-0 bg-[#06b6d4] opacity-20"></div>}
                        {isSystem ? <CheckCircle2 size={18} className="text-[#94a3b8]"/> : <Bot size={20} className="text-[#06b6d4] relative z-10" />}
                      </div>
                    )}
                  </div>

                  {/* Bubble */}
                  <div className={`
                    p-6 rounded-[1.5rem] relative
                    ${isUser 
                      ? "bg-gradient-to-br from-[#7c3aed]/90 to-[#4f46e5]/90 border border-white/10 text-white rounded-tr-sm shadow-[0_15px_30px_rgba(124,58,237,0.3)]" 
                      : msg.tone === "warning"
                        ? "bg-[#f43f5e]/10 border border-[#f43f5e]/30 text-white rounded-tl-sm shadow-[0_15px_30px_rgba(244,63,94,0.15)]"
                        : isResult
                          ? "bg-gradient-to-br from-[#f59e0b]/20 to-[#fb923c]/10 border border-[#f59e0b]/30 text-white rounded-tl-sm shadow-[0_15px_30px_rgba(245,158,11,0.15)]"
                          : isSystem
                            ? "bg-transparent border border-white/5 text-[#94a3b8] text-sm rounded-tl-sm"
                            : "glass-panel border-white/10 text-white rounded-tl-sm shadow-[0_20px_40px_rgba(0,0,0,0.4)] bg-black/40 backdrop-blur-2xl"
                    }
                  `}>
                    {/* Glowing left edge for AI messages */}
                    {!isUser && !isSystem && (
                      <div className="absolute left-0 top-6 bottom-6 w-1 bg-gradient-to-b from-[#06b6d4] to-[#7c3aed] rounded-r-full shadow-[0_0_10px_#06b6d4]"></div>
                    )}

                    {isScenario && (
                      <div className="flex items-center gap-2 mb-4">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#06b6d4]/10 border border-[#06b6d4]/30 rounded-full text-[11px] font-bold text-[#06b6d4] uppercase tracking-[0.15em] shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                          <Zap size={12} className="text-[#06b6d4]" /> Phân tích tình huống
                        </span>
                      </div>
                    )}
                    <p className={`whitespace-pre-line leading-loose ${isSystem ? 'text-sm' : 'text-lg md:text-xl font-medium tracking-tight'}`}>
                      {msg.text}
                    </p>
                  </div>

                </div>
              </div>
            );
          })}

          <SubmitStatus stage={submitStage} />

          {warning && (
            <div className="flex justify-start animate-[slideUp_0.3s_ease-out_forwards]">
              <div className="ml-14 bg-[#f43f5e]/10 border border-[#f43f5e]/30 px-5 py-3 rounded-2xl rounded-tl-sm flex items-center gap-3 shadow-[0_10px_20px_rgba(244,63,94,0.15)]">
                <AlertTriangle size={16} className="text-[#f43f5e]" />
                <p className="text-sm font-medium text-[#f43f5e]">{warning}</p>
              </div>
            </div>
          )}

          {isLoadingProfile && (
            <div className="w-full glass-panel border border-[#06b6d4]/30 bg-gradient-to-br from-[#06b6d4]/5 to-[#7c3aed]/10 p-12 rounded-[2.5rem] text-center shadow-[0_0_50px_rgba(6,182,212,0.15)] relative overflow-hidden animate-[slideUp_0.5s_ease-out_forwards]">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] opacity-50"></div>
              <div className="relative z-10">
                <div className="w-24 h-24 mx-auto mb-8 relative flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-[3px] border-[#06b6d4]/30 border-t-[#06b6d4] animate-spin shadow-[0_0_20px_rgba(6,182,212,0.4)]"></div>
                  <Brain size={32} className="text-[#06b6d4] animate-pulse" />
                </div>
                <h3 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-[#06b6d4] mb-3 tracking-tight uppercase">Đang giải mã dữ liệu</h3>
                <p className="text-[#94a3b8] text-lg max-w-md mx-auto">AI đang tổng hợp mô hình RIASEC và quét cơ sở dữ liệu nghề nghiệp khổng lồ...</p>
              </div>
            </div>
          )}

          {!isLoadingProfile && profile && <ResultPanel profile={profile} />}

          {!isLoadingProfile && !profile && dcpId && (
             <div className="w-full glass-panel border border-[#f43f5e]/30 bg-[#f43f5e]/10 p-10 rounded-[2.5rem] text-center shadow-[0_20px_50px_rgba(244,63,94,0.15)]">
              <div className="w-20 h-20 bg-[#f43f5e]/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertTriangle size={32} className="text-[#f43f5e]" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Hiển thị báo cáo gián đoạn</h3>
              <p className="text-[#94a3b8] mb-8 text-lg">Bài đánh giá đã hoàn tất và lưu trữ thành công, nhưng gặp lỗi khi hiển thị trực tiếp.</p>
              <Link href={`/profile?dcp_id=${dcpId}`} className="btn-premium px-8 py-3 text-lg inline-flex items-center gap-3">
                 <Compass size={20}/> Tới không gian hồ sơ
              </Link>
            </div>
          )}

          <div ref={bottomRef} className="h-20" />
        </div>
      </main>

      {/* Floating Input Dock */}
      <footer
        id="chat-input-bar"
        className="absolute bottom-0 left-0 w-full px-5 py-8 md:px-8 bg-gradient-to-t from-[#030014] via-[#030014]/90 to-transparent z-50 pointer-events-none"
      >
        <div className="max-w-4xl mx-auto relative pointer-events-auto">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#7c3aed] via-[#06b6d4] to-[#c084fc] rounded-[2.5rem] opacity-30 blur-lg transition-opacity duration-500"></div>
          
          <div className="relative flex items-center gap-3 glass-panel border border-white/20 p-2 rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.5)] bg-black/60 backdrop-blur-2xl focus-within:bg-black/80 focus-within:border-white/40 transition-all duration-300">
            <div className="w-12 h-12 flex items-center justify-center shrink-0">
               <MessageSquare size={20} className="text-[#94a3b8]" />
            </div>
            <input
              id="chat-input"
              type="text"
              placeholder={isCompleted ? "Phiên đánh giá đã khóa." : "Nhập phản hồi của bạn..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isInputDisabled}
              className="flex-1 py-4 bg-transparent text-white text-lg font-medium outline-none placeholder-[#94a3b8]/50 disabled:opacity-50 tracking-wide"
            />
            <button
              type="button"
              onClick={() => void handleSend()}
              disabled={isInputDisabled || !input.trim()}
              id="chat-send-btn"
              className="shrink-0 w-14 h-14 rounded-full bg-gradient-to-br from-[#7c3aed] to-[#06b6d4] flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] hover:scale-105 active:scale-95 transition-all cursor-pointer group"
            >
              {isSubmitting ? (
                <LoaderCircle size={24} className="animate-spin" />
              ) : (
                <SendHorizontal size={24} className="ml-1 group-hover:translate-x-1 transition-transform" />
              )}
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

