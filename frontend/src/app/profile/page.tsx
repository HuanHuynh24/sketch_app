import type { Metadata } from "next";
import { Suspense } from "react";
import ProfileClient from "./ProfileClient";

export const metadata: Metadata = {
  title: "SketchApp - Hồ sơ học sinh",
  description: "Hồ sơ học sinh, trạng thái đánh giá RIASEC và các bước định hướng tiếp theo.",
};

export default function ProfilePage() {
  return (
    <Suspense fallback={null}>
      <ProfileClient />
    </Suspense>
  );
}
