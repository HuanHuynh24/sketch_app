"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, HelpCircle, ArrowRight, LoaderCircle } from "lucide-react";
import { ApiError, loginStudent } from "@/lib/api";

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
      await loginStudent({
        email: email.trim(),
        password,
      });

      router.push("/profile");
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
      <div className="flex flex-col gap-2">
        <label
          htmlFor="login-email"
          className="flex items-center gap-2 font-bold text-[#94a3b8] text-sm uppercase tracking-wider"
        >
          <Mail size={16} className="text-[#06b6d4]" /> Email truy cập
        </label>
        <input
          id="login-email"
          type="email"
          placeholder="your.name@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isSubmitting}
          required
          className="bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-[#06b6d4]/50 focus:bg-white/5 transition-all duration-300 placeholder:text-white/20 shadow-inner"
        />
      </div>

      {/* Password */}
      <div className="flex flex-col gap-2">
        <label
          htmlFor="login-password"
          className="flex items-center justify-between gap-2 font-bold text-[#94a3b8] text-sm uppercase tracking-wider"
        >
          <span className="flex items-center gap-2">
             <Lock size={16} className="text-[#c084fc]" /> Mật khẩu
          </span>
          <Link
            href="#"
            className="inline-flex items-center gap-1 text-xs text-[#06b6d4] hover:text-white transition-colors"
          >
            Quên mật khẩu?
          </Link>
        </label>
        <input
          id="login-password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isSubmitting}
          required
          className="bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-[#c084fc]/50 focus:bg-white/5 transition-all duration-300 placeholder:text-white/20 shadow-inner tracking-widest"
        />
      </div>

      {error && (
        <div
          role="alert"
          className="flex items-center gap-3 bg-[#f43f5e]/10 border border-[#f43f5e]/30 px-4 py-3 rounded-xl text-[#f43f5e] text-sm font-medium animate-pulse-slow"
        >
          <HelpCircle size={18} />
          <p>{error}</p>
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        id="login-submit-btn"
        disabled={isSubmitting}
        aria-busy={isSubmitting}
        className="w-full mt-4 btn-premium py-4"
      >
        {isSubmitting ? (
          <span className="flex items-center gap-2"><LoaderCircle className="animate-spin" size={18} /> Đang xác thực...</span>
        ) : (
          <span className="flex items-center justify-center gap-2 text-lg">Khởi động Hành trình <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" /></span>
        )}
      </button>
    </form>
  );
}
