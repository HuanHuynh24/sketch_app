import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SketchApp - Hướng nghiệp AI thông minh",
  description:
    "Hệ thống hướng nghiệp thông minh phân tích năng lực đa chiều để đưa ra lộ trình học tập và chọn trường cá nhân hóa cho từng học sinh.",
  openGraph: {
    title: "SketchApp - Chọn đúng ngành, Sáng tương lai",
    description:
      "AI đánh giá đa chiều giúp bạn tìm ngành học phù hợp nhất.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
