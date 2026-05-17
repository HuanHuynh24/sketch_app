import type { Metadata } from "next";
import AdmissionPrototype from "./AdmissionPrototype";

export const metadata: Metadata = {
  title: "La Bàn Tuyển Sinh - Gợi ý trường đại học cá nhân hóa",
  description:
    "Prototype giao diện Phase 2 cho hệ thống dự đoán tuyển sinh đại học dựa trên điểm số, RIASEC và dữ liệu tuyển sinh.",
};

export default function AdmissionPage() {
  return <AdmissionPrototype />;
}
