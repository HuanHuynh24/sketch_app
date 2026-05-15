"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarDays, Flag, Lock, Mail, MapPin, Palette, Pencil } from "lucide-react";
import { ApiError, registerStudent, saveAuthSession } from "@/lib/api";

export default function SignUpForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [province, setProvince] = useState("");
  const [areaCode, setAreaCode] = useState("");
  const [dob, setDob] = useState("");
  const [priorityGroup, setPriorityGroup] = useState("");
  const [targetProvince, setTargetProvince] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Mật khẩu xác nhận chưa khớp.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await registerStudent({
        full_name: name.trim(),
        email: email.trim(),
        password,
        province: province.trim(),
        area_code: areaCode.trim(),
        dob: dob || undefined,
        priority_group: priorityGroup.trim() || undefined,
        target_province: targetProvince.trim() || undefined,
      });

      saveAuthSession(response);
      // router.push("/chat");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Không thể tạo tài khoản lúc này. Vui lòng thử lại.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const fields = [
    { id: "signup-name", label: "Họ tên", icon: <Pencil size={18} />, type: "text", placeholder: "Nguyen Van Test", value: name, setter: setName, required: true },
    { id: "signup-email", label: "Email", icon: <Mail size={18} />, type: "email", placeholder: "your-sketch@email.com", value: email, setter: setEmail, required: true },
    { id: "signup-password", label: "Mật khẩu", icon: <Lock size={18} />, type: "password", placeholder: "Tạo mật khẩu...", value: password, setter: setPassword, required: true },
    { id: "signup-confirm", label: "Xác nhận mật khẩu", icon: <Lock size={18} />, type: "password", placeholder: "Nhập lại mật khẩu...", value: confirm, setter: setConfirm, required: true },
    { id: "signup-province", label: "Tỉnh/thành hiện tại", icon: <MapPin size={18} />, type: "text", placeholder: "Khánh Hòa", value: province, setter: setProvince, required: true },
    { id: "signup-area-code", label: "Khu vực ưu tiên", icon: <Flag size={18} />, type: "text", placeholder: "KV2", value: areaCode, setter: setAreaCode, required: true },
    { id: "signup-dob", label: "Ngày sinh", icon: <CalendarDays size={18} />, type: "date", placeholder: "", value: dob, setter: setDob, required: false },
    { id: "signup-priority-group", label: "Nhóm ưu tiên", icon: <Flag size={18} />, type: "text", placeholder: "01", value: priorityGroup, setter: setPriorityGroup, required: false },
    { id: "signup-target-province", label: "Tỉnh/thành muốn học", icon: <MapPin size={18} />, type: "text", placeholder: "TP.HCM", value: targetProvince, setter: setTargetProvince, required: false },
  ];

  return (
    <form className="flex flex-col gap-5" onSubmit={handleSubmit} id="signup-form">
      {fields.map(({ id, label, icon, type, placeholder, value, setter, required }) => (
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
            required={required}
            disabled={isSubmitting}
            className="bg-transparent border-0 border-b-[3px] border-sketch-ink px-0 py-2.5 text-lg outline-none focus:border-sketch-blue transition-colors duration-150 placeholder:text-sketch-muted placeholder:italic"
            style={{ fontFamily: "var(--font-body)" }}
          />
        </div>
      ))}

      {error && (
        <p
          role="alert"
          className="border-[2px] border-sketch-error bg-red-50 px-4 py-2 text-sketch-error"
        >
          {error}
        </p>
      )}

      <button
        type="submit"
        id="signup-submit-btn"
        disabled={isSubmitting}
        aria-busy={isSubmitting}
        className="w-full inline-flex items-center justify-center gap-2 py-3 mt-2 text-white font-bold border-[2px] border-sketch-ink bg-sketch-blue wobbly-btn shadow-sketch-blue text-lg cursor-pointer transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1 disabled:cursor-not-allowed disabled:opacity-60"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        <Palette size={18} /> {isSubmitting ? "Đang tạo tài khoản..." : "Tạo tài khoản"}
      </button>
    </form>
  );
}
