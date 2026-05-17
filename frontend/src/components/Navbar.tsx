"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ChevronDown, Compass, LogOut, UserRound } from "lucide-react";
import { clearAuthSession, getAccessToken, getStoredStudent } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [studentName, setStudentName] = useState("");

  useEffect(() => {
    const student = getStoredStudent();
    setIsLoggedIn(Boolean(getAccessToken()));
    setStudentName(student?.full_name ?? "");
  }, [pathname]);

  const handleLogout = () => {
    clearAuthSession();
    setIsLoggedIn(false);
    setStudentName("");
    router.push("/login");
  };

  const navItems = [
    { href: "/#features", label: "Lộ trình" },
    { href: "/chat", label: "RIASEC" },
  ];

  const accountLabel = studentName ? studentName.split(" ").slice(-2).join(" ") : "Tài khoản";

  return (
    <nav
      id="navbar"
      className="sticky top-0 z-50 flex items-center justify-between px-5 md:px-8 py-3 bg-sketch-bg border-b-[3px] border-sketch-ink"
      style={{ fontFamily: "var(--font-body)" }}
    >
      <Link
        href="/"
        id="nav-logo"
        className="flex items-center gap-2 text-sketch-red no-underline hover:no-underline"
        style={{ fontFamily: "var(--font-heading)", fontSize: 26, fontWeight: 700 }}
      >
        <svg viewBox="0 0 32 32" fill="none" className="w-8 h-8 flex-shrink-0">
          <rect x="2" y="2" width="28" height="28" rx="4" stroke="#2d2d2d" strokeWidth="2.5" fill="#fff385" />
          <path d="M8 22 C10 14, 14 10, 16 16 C18 22, 22 8, 24 12" stroke="#ff4d4d" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          <circle cx="10" cy="10" r="2" fill="#2d5da1" />
        </svg>
        SketchApp
      </Link>

      <ul id="nav-links" className="hidden md:flex items-center gap-4 list-none m-0 p-0">
        {navItems.map(({ href, label }) => (
          <li key={href}>
            <Link
              href={href}
              className={`text-sketch-ink no-underline text-lg px-3 py-1.5 rounded-lg inline-block transition-colors duration-150 hover:bg-sketch-bg-alt hover:no-underline ${
                pathname === href ? "bg-sketch-yellow border-[2px] border-sketch-ink" : ""
              }`}
            >
              {label}
            </Link>
          </li>
        ))}

        <li>
          {isLoggedIn ? (
            <div className="group relative">
              <button
                type="button"
                className="inline-flex items-center gap-2 px-4 py-2 font-bold text-sketch-blue bg-sketch-surface border-[2px] border-sketch-ink wobbly-btn shadow-sketch text-sm cursor-pointer"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                <UserRound size={15} />
                <span className="max-w-32 truncate">{accountLabel}</span>
                <ChevronDown size={15} className="transition-transform duration-150 group-hover:rotate-180" />
              </button>

              <div className="absolute right-0 top-full hidden min-w-44 pt-2 group-hover:block">
                <div className="bg-sketch-surface border-[2px] border-sketch-ink shadow-sketch rounded-lg overflow-hidden">
                  <Link
                    href="/profile"
                    className="flex items-center gap-2 px-4 py-3 text-sm font-bold text-sketch-ink no-underline hover:no-underline hover:bg-sketch-yellow"
                    style={{ fontFamily: "var(--font-heading)" }}
                  >
                    <UserRound size={15} />
                    Xem hồ sơ
                  </Link>
                  <Link
                    href="/admission"
                    className="flex items-center gap-2 px-4 py-3 text-sm font-bold text-sketch-ink no-underline hover:no-underline hover:bg-sketch-yellow"
                    style={{ fontFamily: "var(--font-heading)" }}
                  >
                    <Compass size={15} />
                    La bàn
                  </Link>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm font-bold text-sketch-red bg-sketch-surface hover:bg-red-50 cursor-pointer"
                    style={{ fontFamily: "var(--font-heading)" }}
                  >
                    <LogOut size={15} />
                    Đăng xuất
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <Link
              href="/login"
              id="nav-login-btn"
              className="inline-flex items-center gap-1.5 px-5 py-2 font-bold text-white bg-sketch-red border-[2px] border-sketch-ink wobbly-btn shadow-sketch text-base no-underline transition-all duration-100 hover:no-underline active:shadow-pressed active:translate-x-0.5 active:translate-y-0.5"
              style={{ fontFamily: "var(--font-heading)", fontSize: 15 }}
            >
              Đăng nhập
            </Link>
          )}
        </li>
      </ul>

      <Link
        href={isLoggedIn ? "/profile" : "/login"}
        className="md:hidden inline-flex items-center px-4 py-2 font-bold text-white bg-sketch-red border-[2px] border-sketch-ink wobbly-btn shadow-sketch text-sm no-underline"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        {isLoggedIn ? accountLabel : "Đăng nhập"}
      </Link>
    </nav>
  );
}
