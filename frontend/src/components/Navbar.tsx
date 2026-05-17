import Link from "next/link";

export default function Navbar() {
  return (
    <nav
      id="navbar"
      className="sticky top-0 z-50 flex items-center justify-between px-8 py-3 bg-sketch-bg border-b-[3px] border-sketch-ink"
      style={{ fontFamily: "var(--font-body)" }}
    >
      {/* Logo */}
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

      {/* Nav links */}
      <ul id="nav-links" className="flex items-center gap-5 list-none m-0 p-0">
        {[
          { href: "/#features", label: "Pathways" },
          { href: "/chat",      label: "AI Insights" },
          { href: "/admission", label: "La Bàn" },
          { href: "/profile",   label: "Hồ sơ" },
        ].map(({ href, label }) => (
          <li key={href}>
            <Link
              href={href}
              className="text-sketch-ink no-underline text-lg px-3 py-1.5 rounded-lg inline-block transition-colors duration-150 hover:bg-sketch-bg-alt hover:no-underline"
            >
              {label}
            </Link>
          </li>
        ))}

        <li>
          <Link
            href="/login"
            id="nav-login-btn"
            className="inline-flex items-center gap-1.5 px-5 py-2 font-bold text-white bg-sketch-red border-[2px] border-sketch-ink wobbly-btn shadow-sketch text-base no-underline transition-all duration-100 hover:no-underline active:shadow-pressed active:translate-x-0.5 active:translate-y-0.5"
            style={{ fontFamily: "var(--font-heading)", fontSize: 15 }}
          >
            Đăng nhập
          </Link>
        </li>
      </ul>
    </nav>
  );
}
