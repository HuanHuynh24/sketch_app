import type { Metadata } from "next";
import Link from "next/link";
import LoginForm from "./LoginForm";
import Navbar from "@/components/Navbar";
import { Pencil } from "lucide-react";

export const metadata: Metadata = {
  title: "SketchApp - Login",
  description: "Đăng nhập vào SketchApp để bắt đầu hành trình hướng nghiệp AI.",
};

export default function LoginPage() {
  return (
    <>
      <Navbar />
      {/* Full-screen centering */}
      <div className="min-h-[calc(100vh-73px)] flex items-center justify-center px-6 py-12">
        <div
          id="login-card"
          className="relative w-full max-w-md bg-sketch-surface border-[3px] border-sketch-ink wobbly shadow-sketch-lg px-10 py-12 -rotate-[0.5deg] pinned"
        >
          <h1 className="text-center text-sketch-red mb-1" style={{ fontFamily: "var(--font-heading)" }}>Login</h1>
          <p className="flex items-center justify-center gap-1.5 text-center text-sketch-muted text-lg mb-8">
            Ready to doodle your dreams? <Pencil size={18} />
          </p>

          <LoginForm />

          <p className="text-center mt-6 text-base text-sketch-muted">
            Don&apos;t have a canvas?{" "}
            <Link href="/signup" id="login-signup-link" className="text-sketch-blue">Sign Up</Link>
          </p>

          <div className="flex justify-center gap-6 mt-6 text-sm text-sketch-muted">
            <Link href="#">Privacy</Link>
            <Link href="#">Terms</Link>
            <Link href="#">Support</Link>
          </div>

          <p className="text-center mt-4 text-sm text-sketch-muted">© 2024 Hand-Drawn Inc.</p>
        </div>
      </div>
    </>
  );
}
