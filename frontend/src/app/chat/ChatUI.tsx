"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import { Bot, User, SendHorizontal, MessageSquare } from "lucide-react";

interface Message {
  id: number;
  role: "ai" | "user";
  text: string;
}

const initialMessages: Message[] = [
  { id: 1, role: "ai",   text: "Chào mừng bạn! Tôi có thể giúp bạn đánh giá các kỹ năng tư duy logic thông qua các câu hỏi tình huống. Chúng ta bắt đầu nhé?" },
  { id: 2, role: "user", text: "Sẵn sàng! Hãy cho tôi một bài toán tư duy thú vị về quản lý thời gian." },
  { id: 3, role: "ai",   text: '"Bạn có 3 việc quan trọng nhưng chỉ có đủ năng lượng cho 1 việc duy nhất trong sáng nay."\n\nDựa trên tình huống này, bạn sẽ chọn cách tiếp cận nào để tối ưu hóa hiệu suất?' },
];

export default function ChatUI() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg: Message = { id: messages.length + 1, role: "user", text: input };
    const aiReply: Message = {
      id: messages.length + 2,
      role: "ai",
      text: "Tuyệt vời! Đó là một cách tiếp cận rất logic. Bạn đang thể hiện khả năng ưu tiên hóa tốt — đây là một trong những kỹ năng quan trọng nhất trong nhóm ngành Quản trị và Công nghệ. Hãy thử câu tiếp theo nhé!",
    };
    setMessages((prev) => [...prev, userMsg, aiReply]);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Navbar */}
      <Navbar />

      {/* Chat sub-header */}
      <div
        id="chat-header"
        className="flex items-center gap-3 px-8 py-4 border-b-[3px] border-sketch-ink bg-sketch-bg"
      >
        <MessageSquare size={22} className="text-sketch-red" />
        <h2 className="text-sketch-red m-0" style={{ fontFamily: "var(--font-heading)", fontSize: 22 }}>
          Hội thoại AI - Khám phá Năng lực
        </h2>
      </div>

      {/* Messages */}
      <div id="chat-messages" className="flex-1 overflow-y-auto px-8 py-6 flex flex-col gap-5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            id={`chat-msg-${msg.id}`}
            className={`max-w-[70%] px-5 py-4 border-[2px] border-sketch-ink text-lg leading-relaxed ${
              msg.role === "ai"
                ? "self-start bg-sketch-surface shadow-sketch -rotate-[0.5deg] rounded-tl-sm rounded-tr-2xl rounded-br-2xl rounded-bl-2xl"
                : "self-end bg-sketch-blue text-white shadow-sketch-blue rotate-[0.5deg] rounded-tl-2xl rounded-tr-sm rounded-br-2xl rounded-bl-2xl"
            }`}
          >
            <div
              className={`flex items-center gap-1 text-sm font-bold mb-1 opacity-70 ${msg.role === "ai" ? "text-sketch-ink" : "text-white"}`}
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {msg.role === "ai" ? <><Bot size={14} /> SketchAI</> : <><User size={14} /> Bạn</>}
            </div>
            <p style={{ whiteSpace: "pre-line" }}>{msg.text}</p>
          </div>
        ))}
      </div>

      {/* Input bar */}
      <div
        id="chat-input-bar"
        className="flex gap-4 px-8 py-4 border-t-[3px] border-sketch-ink bg-sketch-bg"
      >
        <input
          id="chat-input"
          type="text"
          placeholder="Nhập câu trả lời của bạn..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 px-5 py-3 border-[2px] border-sketch-ink wobbly-alt bg-sketch-surface text-lg outline-none focus:border-sketch-blue focus:shadow-sketch-blue transition-all duration-150"
          style={{ fontFamily: "var(--font-body)" }}
        />
        <button
          onClick={handleSend}
          id="chat-send-btn"
          className="inline-flex items-center gap-2 px-6 py-3 text-white font-bold border-[2px] border-sketch-ink bg-sketch-red wobbly-btn shadow-sketch text-lg cursor-pointer transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          <SendHorizontal size={18} /> Gửi
        </button>
      </div>
    </div>
  );
}
