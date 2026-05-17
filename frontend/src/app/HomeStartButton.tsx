"use client";

import { useRouter } from "next/navigation";
import { Pencil } from "lucide-react";
import { getAccessToken } from "@/lib/api";

type HomeStartButtonProps = {
  id: string;
  className: string;
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
      className={className}
      style={{ fontFamily: "var(--font-heading)" }}
    >
      <Pencil size={20} /> Bắt đầu ngay
    </button>
  );
}
