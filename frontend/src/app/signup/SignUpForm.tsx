"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarDays, Flag, Lock, Mail, MapPin, Palette, User, Target, LoaderCircle, CheckCircle2, AlertTriangle } from "lucide-react";
import { ApiError, registerStudent } from "@/lib/api";

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
      setError("Mật khẩu xác nhận chưa khớp. Vui lòng kiểm tra lại.");
      return;
    }

    setIsSubmitting(true);

    try {
      await registerStudent({
        full_name: name.trim(),
        email: email.trim(),
        password,
        province: province.trim(),
        area_code: areaCode.trim(),
        dob: dob || undefined,
        priority_group: priorityGroup.trim() || undefined,
        target_province: targetProvince.trim() || undefined,
      });

      router.push("/chat");
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

  const basicFields = [
    { id: "signup-name", label: "Họ và Tên", icon: <User size={16} className="text-[#06b6d4]" />, type: "text", placeholder: "Nguyễn Văn An", value: name, setter: setName, required: true },
    { id: "signup-email", label: "Email truy cập", icon: <Mail size={16} className="text-[#8b5cf6]" />, type: "email", placeholder: "your.name@example.com", value: email, setter: setEmail, required: true },
    { id: "signup-password", label: "Mật khẩu bảo mật", icon: <Lock size={16} className="text-[#f59e0b]" />, type: "password", placeholder: "••••••••", value: password, setter: setPassword, required: true },
    { id: "signup-confirm", label: "Xác nhận mật khẩu", icon: <CheckCircle2 size={16} className="text-[#10b981]" />, type: "password", placeholder: "••••••••", value: confirm, setter: setConfirm, required: true },
  ];

  const detailFields = [
    { id: "signup-province", label: "Tỉnh/thành hiện tại", icon: <MapPin size={16} className="text-[#f43f5e]" />, type: "text", placeholder: "VD: Khánh Hòa", value: province, setter: setProvince, required: true },
    { id: "signup-area-code", label: "Khu vực ưu tiên", icon: <Flag size={16} className="text-[#c084fc]" />, type: "text", placeholder: "VD: KV2", value: areaCode, setter: setAreaCode, required: true },
    { id: "signup-dob", label: "Ngày sinh (Không bắt buộc)", icon: <CalendarDays size={16} className="text-white/50" />, type: "date", placeholder: "", value: dob, setter: setDob, required: false },
    { id: "signup-priority-group", label: "Nhóm ưu tiên (Nếu có)", icon: <Flag size={16} className="text-white/50" />, type: "text", placeholder: "VD: 01", value: priorityGroup, setter: setPriorityGroup, required: false },
    { id: "signup-target-province", label: "Tỉnh/thành mục tiêu", icon: <Target size={16} className="text-white/50" />, type: "text", placeholder: "VD: TP.HCM", value: targetProvince, setter: setTargetProvince, required: false },
  ];

  const renderField = ({ id, label, icon, type, placeholder, value, setter, required }: any) => (
    <div key={id} className="flex flex-col gap-2">
      <label
        htmlFor={id}
        className="flex items-center gap-2 font-bold text-[#94a3b8] text-[13px] uppercase tracking-wider"
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
        className="bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-[#06b6d4]/50 focus:bg-white/5 transition-all duration-300 placeholder:text-white/20 shadow-inner"
      />
    </div>
  );

  return (
    <form className="flex flex-col gap-8" onSubmit={handleSubmit} id="signup-form">
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex flex-col gap-6">
           <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-full bg-[#06b6d4]/20 border border-[#06b6d4]/30 flex items-center justify-center text-[#06b6d4] font-bold">1</div>
              <h3 className="text-white font-bold text-lg">Thông tin định danh</h3>
           </div>
           {basicFields.map(renderField)}
        </div>
        
        <div className="flex flex-col gap-6">
           <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-full bg-[#c084fc]/20 border border-[#c084fc]/30 flex items-center justify-center text-[#c084fc] font-bold">2</div>
              <h3 className="text-white font-bold text-lg">Hồ sơ tuyển sinh</h3>
           </div>
           {detailFields.map(renderField)}
        </div>
      </div>

      {error && (
        <div
          role="alert"
          className="flex items-center gap-3 bg-[#f43f5e]/10 border border-[#f43f5e]/30 px-4 py-3 rounded-xl text-[#f43f5e] text-sm font-medium animate-pulse-slow mx-auto w-full max-w-2xl"
        >
          <AlertTriangle size={18} />
          <p>{error}</p>
        </div>
      )}

      <button
        type="submit"
        id="signup-submit-btn"
        disabled={isSubmitting}
        aria-busy={isSubmitting}
        className="w-full md:w-auto md:min-w-[300px] mx-auto mt-4 btn-premium py-4"
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center gap-2"><LoaderCircle className="animate-spin" size={18} /> Đang khởi tạo hồ sơ...</span>
        ) : (
          <span className="flex items-center justify-center gap-2 text-lg"><Palette size={20} /> Thiết lập Hồ Sơ & Tham gia</span>
        )}
      </button>
    </form>
  );
}
