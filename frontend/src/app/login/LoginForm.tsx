"use client";

import { useState } from "react";
import Link from "next/link";
import { Mail, Lock, HelpCircle, ArrowRight } from "lucide-react";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Logging in with: ${email}`);
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

      {/* Submit */}
      <button
        type="submit"
        id="login-submit-btn"
        className="w-full inline-flex items-center justify-center gap-2 py-3 text-white font-bold border-[2px] border-sketch-ink bg-sketch-red wobbly-btn shadow-sketch text-lg cursor-pointer transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        <ArrowRight size={18} /> Click Here!
      </button>
    </form>
  );
}
