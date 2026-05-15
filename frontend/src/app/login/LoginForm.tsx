"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, HelpCircle, ArrowRight } from "lucide-react";
import { ApiError, loginStudent, saveAuthSession } from "@/lib/api";

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await loginStudent({
        email: email.trim(),
        password,
      });

      saveAuthSession(response);
      router.push("/chat");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Không thể đăng nhập lúc này. Vui lòng thử lại.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="flex flex-col gap-6" onSubmit={handleSubmit} id="login-form">
      {/* Email */}
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="login-email"
          className="flex items-center gap-1.5 font-bold text-sketch-ink"
          style={{ fontFamily: "var(--font-heading)", fontSize: 18 }}
        >
          <Mail size={18} /> Email
        </label>
        <input
          id="login-email"
          type="email"
          placeholder="your-sketch@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isSubmitting}
          required
          className="bg-transparent border-0 border-b-[3px] border-sketch-ink px-0 py-3 text-lg outline-none focus:border-sketch-blue transition-colors duration-150 placeholder:text-sketch-muted placeholder:italic"
          style={{ fontFamily: "var(--font-body)" }}
        />
      </div>

      {/* Password */}
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="login-password"
          className="flex items-center gap-1.5 font-bold text-sketch-ink"
          style={{ fontFamily: "var(--font-heading)", fontSize: 18 }}
        >
          <Lock size={18} /> Password
        </label>
        <input
          id="login-password"
          type="password"
          placeholder="your secret doodle..."
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isSubmitting}
          required
          className="bg-transparent border-0 border-b-[3px] border-sketch-ink px-0 py-3 text-lg outline-none focus:border-sketch-blue transition-colors duration-150 placeholder:text-sketch-muted placeholder:italic"
          style={{ fontFamily: "var(--font-body)" }}
        />
      </div>

      {/* Forgot */}
      <div className="text-right">
        <Link
          href="#"
          className="inline-flex items-center gap-1 text-base text-sketch-red hover:no-underline hover:opacity-80"
        >
          <HelpCircle size={14} /> Forgot Pass?
        </Link>
      </div>

      {error && (
        <p
          role="alert"
          className="border-[2px] border-sketch-error bg-red-50 px-4 py-2 text-sketch-error"
        >
          {error}
        </p>
      )}

      {/* Submit */}
      <button
        type="submit"
        id="login-submit-btn"
        disabled={isSubmitting}
        aria-busy={isSubmitting}
        className="w-full inline-flex items-center justify-center gap-2 py-3 text-white font-bold border-[2px] border-sketch-ink bg-sketch-red wobbly-btn shadow-sketch text-lg cursor-pointer transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1 disabled:cursor-not-allowed disabled:opacity-60"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        <ArrowRight size={18} /> {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
      </button>
    </form>
  );
}
