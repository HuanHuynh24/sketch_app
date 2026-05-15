import type { Metadata } from "next";
import Link from "next/link";
import SignUpForm from "./SignUpForm";
import Navbar from "@/components/Navbar";
import { PenLine } from "lucide-react";

export const metadata: Metadata = {
  title: "SketchApp - Sign Up",
  description: "Tạo tài khoản SketchApp và bắt đầu hành trình sáng tạo của bạn.",
};

export default function SignUpPage() {
  return (
    <>
      <Navbar />
      <div className="min-h-[calc(100vh-73px)] flex items-center justify-center px-6 py-12">
        <div
          id="signup-card"
          className="relative w-full max-w-xl bg-sketch-surface border-[3px] border-sketch-ink wobbly shadow-sketch-lg px-10 py-12 rotate-[0.5deg] pinned"
        >
          <h1 className="text-center text-sketch-red mb-1" style={{ fontFamily: "var(--font-heading)" }}>
            Join the Sketchbook
          </h1>
          <p className="flex items-center justify-center gap-1.5 text-center text-sketch-muted text-lg mb-8">
            Your creative journey starts with a single line. <PenLine size={18} />
          </p>

          <SignUpForm />

          <p className="text-center mt-6 text-base text-sketch-muted">
            Already sketching?{" "}
            <Link href="/login" id="signup-login-link" className="text-sketch-blue">Sign In</Link>
          </p>

          <div className="flex justify-center gap-6 mt-4 text-sm text-sketch-muted">
            <Link href="#">Privacy</Link>
            <Link href="#">Terms</Link>
            <Link href="#">Support</Link>
          </div>
        </div>
      </div>
    </>
  );
}
