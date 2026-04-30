import Link from "next/link";

export default function Footer() {
  return (
    <footer
      id="footer"
      className="text-center px-8 py-10 border-t-[3px] border-dashed border-sketch-ink mt-16 bg-sketch-bg"
    >
      <p style={{ fontFamily: "var(--font-heading)", fontSize: 20 }}>
        © 2024 Hand-Drawn Inc.
      </p>
      <div className="flex justify-center gap-8 mt-4 flex-wrap">
        {["Privacy Policy", "Terms of Scribble", "Contact Us"].map((label) => (
          <Link
            key={label}
            href="#"
            className="text-sketch-muted text-base hover:text-sketch-blue transition-colors duration-150"
          >
            {label}
          </Link>
        ))}
      </div>
    </footer>
  );
}
