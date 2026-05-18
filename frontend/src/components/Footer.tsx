import Link from "next/link";

export default function Footer() {
  return (
    <footer
      id="footer"
      className="text-center px-8 py-10 border-t border-white/10 mt-16 bg-[#030014]/50 backdrop-blur-md relative z-10"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
      <p style={{ fontFamily: "var(--font-heading)", fontSize: 20 }} className="text-white font-bold tracking-tight">
        © 2026 SketchApp AI
      </p>
      <div className="flex justify-center gap-8 mt-4 flex-wrap">
        {["Privacy Policy", "Terms of Service", "Contact Us"].map((label) => (
          <Link
            key={label}
            href="#"
            className="text-[#94a3b8] text-sm font-medium hover:text-white transition-colors duration-150"
          >
            {label}
          </Link>
        ))}
      </div>
    </footer>
  );
}
