import type { Metadata } from "next";
import ChatUI from "./ChatUI";

export const metadata: Metadata = {
  title: "SketchApp - Hội thoại AI",
  description: "Trò chuyện với AI để khám phá năng lực và nhận tư vấn hướng nghiệp cá nhân hóa.",
};

export default function ChatPage() {
  return <ChatUI />;
}
