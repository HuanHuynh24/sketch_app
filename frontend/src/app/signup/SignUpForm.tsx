"use client";

import { useState } from "react";
import { Pencil, Mail, Lock, Palette } from "lucide-react";

export default function SignUpForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) { alert("Passwords don't match!"); return; }
    alert(`Creating account for: ${name} (${email})`);
  };

  const fields = [
    { id: "signup-name",    label: "Your Name",       icon: <Pencil size={18} />, type: "text",     placeholder: "What should we call you?", value: name,     setter: setName },
    { id: "signup-email",   label: "Email",            icon: <Mail size={18} />,   type: "email",    placeholder: "your-sketch@email.com",    value: email,    setter: setEmail },
    { id: "signup-password",label: "Password",         icon: <Lock size={18} />,   type: "password", placeholder: "Create a secret doodle...", value: password, setter: setPassword },
    { id: "signup-confirm", label: "Confirm Password", icon: <Lock size={18} />,   type: "password", placeholder: "Draw it again...",          value: confirm,  setter: setConfirm },
  ];

  return (
    <form className="flex flex-col gap-5" onSubmit={handleSubmit} id="signup-form">
      {fields.map(({ id, label, icon, type, placeholder, value, setter }) => (
        <div key={id} className="flex flex-col gap-1.5">
          <label
            htmlFor={id}
            className="flex items-center gap-1.5 font-bold text-sketch-ink"
            style={{ fontFamily: "var(--font-heading)", fontSize: 17 }}
          >
            {icon} {label}
          </label>
          <input
            id={id}
            type={type}
            placeholder={placeholder}
            value={value}
            onChange={(e) => setter(e.target.value)}
            required
            className="bg-transparent border-0 border-b-[3px] border-sketch-ink px-0 py-2.5 text-lg outline-none focus:border-sketch-blue transition-colors duration-150 placeholder:text-sketch-muted placeholder:italic"
            style={{ fontFamily: "var(--font-body)" }}
          />
        </div>
      ))}

      <button
        type="submit"
        id="signup-submit-btn"
        className="w-full inline-flex items-center justify-center gap-2 py-3 mt-2 text-white font-bold border-[2px] border-sketch-ink bg-sketch-blue wobbly-btn shadow-sketch-blue text-lg cursor-pointer transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        <Palette size={18} /> Join the Sketchbook
      </button>
    </form>
  );
}
