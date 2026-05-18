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
      className="sticky top-0 z-50 flex items-center justify-between px-5 md:px-8 py-4 glass-nav transition-all"
    >
      <Link
        href="/"
        id="nav-logo"
        className="flex items-center gap-2 text-white no-underline hover:no-underline font-bold text-2xl tracking-tight"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#7c3aed] to-[#06b6d4] p-[2px]">
          <div className="w-full h-full bg-[#030014] rounded-[10px] flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-white">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#paint0_linear)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <defs>
                <linearGradient id="paint0_linear" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#c084fc" />
                  <stop offset="1" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        Sketch<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#c084fc] to-[#06b6d4]">App</span>
      </Link>

      <ul id="nav-links" className="hidden md:flex items-center gap-2 list-none m-0 p-0">
        {navItems.map(({ href, label }) => (
          <li key={href}>
            <Link
              href={href}
              className={`text-sm font-medium px-4 py-2 rounded-full transition-all duration-300 hover:text-white hover:bg-white/10 ${
                pathname === href ? "bg-white/10 text-white" : "text-[#94a3b8]"
              }`}
            >
              {label}
            </Link>
          </li>
        ))}

        <li className="ml-2">
          {isLoggedIn ? (
            <div className="group relative">
              <button
                type="button"
                className="btn-glass inline-flex items-center gap-2 px-5 py-2 text-sm cursor-pointer"
              >
                <UserRound size={16} className="text-[#06b6d4]" />
                <span className="max-w-32 truncate">{accountLabel}</span>
                <ChevronDown size={14} className="transition-transform duration-300 group-hover:rotate-180 text-white/50" />
              </button>

              <div className="absolute right-0 top-full hidden min-w-[200px] pt-3 group-hover:block transition-all opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0">
                <div className="glass-panel border-white/10 overflow-hidden py-1">
                  <Link
                    href="/profile"
                    className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    <UserRound size={16} className="text-[#c084fc]" />
                    Xem hồ sơ
                  </Link>
                  <Link
                    href="/admission"
                    className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    <Compass size={16} className="text-[#06b6d4]" />
                    La bàn tuyển sinh
                  </Link>
                  <div className="h-px bg-white/10 my-1"></div>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm font-medium text-[#f43f5e] hover:bg-[#f43f5e]/10 transition-colors"
                  >
                    <LogOut size={16} />
                    Đăng xuất
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <Link
              href="/login"
              id="nav-login-btn"
              className="btn-premium inline-flex items-center gap-2 px-6 py-2 text-sm no-underline hover:text-white shadow-[0_0_15px_rgba(124,58,237,0.3)]"
            >
              Đăng nhập
            </Link>
          )}
        </li>
      </ul>

      <Link
        href={isLoggedIn ? "/profile" : "/login"}
        className="md:hidden btn-premium inline-flex items-center px-5 py-2 text-sm no-underline"
      >
        {isLoggedIn ? accountLabel : "Đăng nhập"}
      </Link>
    </nav>
  );
}
