"use client";

import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
import { getAccessToken } from "@/lib/api";

type HomeStartButtonProps = {
  id: string;
  className?: string;
};

export default function HomeStartButton({ id, className }: HomeStartButtonProps) {
  const router = useRouter();

  const handleStart = () => {
    router.push(getAccessToken() ? "/chat" : "/login");
  };

  return (
    <button
      type="button"
      id={id}
      onClick={handleStart}
      className={`btn-premium inline-flex items-center justify-center gap-2 px-8 py-4 text-white text-lg transition-all ${className}`}
    >
      <Sparkles size={20} className="animate-pulse-glow" /> 
      <span>Bắt đầu ngay</span>
    </button>
  );
}
