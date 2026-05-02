import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";
import {
  Brain, BarChart3, Target, GraduationCap, TrendingUp,
  Bot, Radio, Database, Backpack, Users, School,
  Pencil, BookOpen, Star, CheckCircle2,
} from "lucide-react";

export default function Home() {
  return (
    <>
      <Navbar />

      {/* Hero */}
      <section id="hero" className="text-center py-16 px-8 relative">
        <h1 className="-rotate-1 mb-4">
          Chọn đúng ngành,{" "}
          <span className="highlight">Sáng tương lai</span>
        </h1>
        <p className="text-sketch-muted text-xl max-w-2xl mx-auto mb-8" style={{ fontFamily: "var(--font-body)" }}>
          Hệ thống hướng nghiệp thông minh phân tích năng lực đa chiều để đưa
          ra lộ trình học tập và chọn trường cá nhân hóa cho từng học sinh.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link
            href="/signup"
            id="hero-cta-signup"
            className="inline-flex items-center gap-2 px-10 py-4 text-white font-bold border-[2px] border-sketch-ink bg-sketch-red wobbly-btn shadow-sketch text-xl hover:no-underline transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            <Pencil size={20} /> Bắt đầu miễn phí
          </Link>
          <Link
            href="#how-it-works"
            id="hero-cta-learn"
            className="inline-flex items-center gap-2 px-10 py-4 font-bold border-[2px] border-sketch-ink bg-sketch-surface wobbly-btn shadow-sketch text-xl hover:no-underline transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            <BookOpen size={20} /> Tìm hiểu thêm
          </Link>
        </div>
      </section>

      <hr className="hand-drawn-hr" />

      {/* Pain Points */}
      <section id="pain-points" className="py-16 px-8 max-w-5xl mx-auto">
        <h2 className="text-center mb-10 rotate-[0.5deg]">Bạn có đang cảm thấy như thế này?</h2>
        <div className="max-w-2xl mx-auto space-y-3">
          {[
            "Em thích vẽ nhưng bố mẹ muốn em học Kinh tế vì dễ xin việc.",
            "Ngành CNTT lấy điểm cao quá, không biết em có cửa đỗ không?",
            "Có quá nhiều trường, em không biết chọn trường nào phù hợp nhất.",
            "Sợ học xong ra trường lại thất nghiệp hoặc làm trái ngành.",
            "Cảm thấy lạc lõng vì không biết bản thân mình thực sự giỏi cái gì.",
          ].map((text) => (
            <div
              key={text}
              className="italic px-5 py-3 border-l-4 border-sketch-red bg-red-50/50 rounded-r-lg -rotate-[0.3deg] text-lg"
              style={{ fontFamily: "var(--font-body)" }}
            >
              &ldquo;{text}&rdquo;
            </div>
          ))}
        </div>
        <p className="text-center text-sketch-muted text-xl max-w-2xl mx-auto mt-10">
          Đừng để cảm xúc nhất thời hay áp lực gia đình dẫn dắt tương lai. Hãy để{" "}
          <span className="highlight">Dữ liệu thực tế</span> giúp bạn quyết định.
        </p>
      </section>

      <hr className="hand-drawn-hr" />

      {/* Features */}
      <section id="features" className="py-16 px-8 max-w-5xl mx-auto">
        <h2 className="text-center mb-10 -rotate-[0.5deg]">Chúng tôi giúp bạn như thế nào?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { id: "feature-1", icon: <Brain size={40} strokeWidth={1.5} />, title: "Hiểu bạn là ai", desc: 'AI đánh giá đa chiều: Logic, EQ, Sáng tạo và tính cách để tìm ra "vùng an toàn" và "vùng phát triển" của bạn.', rotate: "rotate-[1deg]" },
            { id: "feature-2", icon: <BarChart3 size={40} strokeWidth={1.5} />, title: "Dữ liệu thật", desc: "Phân tích hàng triệu điểm dữ liệu tuyển sinh từ các trường Đại học trong 10 năm qua để đưa ra dự báo chính xác.", rotate: "-rotate-[1deg]" },
            { id: "feature-3", icon: <Target size={40} strokeWidth={1.5} />, title: "Chiến lược rõ ràng", desc: "Cung cấp lộ trình ôn thi, các môn cần tập trung và danh sách nguyện vọng thông minh để tối ưu khả năng đỗ.", rotate: "rotate-[1deg]" },
          ].map(({ id, icon, title, desc, rotate }) => (
            <div
              key={id}
              id={id}
              className={`relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 text-center tape transition-all duration-200 hover:-translate-y-1 hover:shadow-sketch-lg ${rotate}`}
            >
              <div className="flex justify-center mb-4 text-sketch-blue">{icon}</div>
              <h3 className="text-sketch-blue mb-2">{title}</h3>
              <p className="text-sketch-muted">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="section-alt-bg py-16 px-8">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-center mb-10">Hành trình 3 bước</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { id: "step-1", num: "01", title: "AI Assessment", desc: "Làm bài kiểm tra năng lực toàn diện: Logic, Ngôn ngữ, EQ, Sáng tạo.", rotate: "-rotate-[1deg]" },
              { id: "step-2", num: "02", title: "Recommendations", desc: "AI đối chiếu năng lực với 6 nhóm nghề nghiệp RIASEC để tìm ngành phù hợp.", rotate: "rotate-[1deg]" },
              { id: "step-3", num: "03", title: "Admission Prediction", desc: "Dự đoán tỉ lệ trúng tuyển vào các trường mục tiêu dựa trên điểm thi.", rotate: "-rotate-[1deg]" },
            ].map(({ id, num, title, desc, rotate }) => (
              <div
                key={id}
                id={id}
                className={`bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 flex gap-4 items-start transition-all duration-200 hover:-translate-y-1 ${rotate}`}
              >
                <div className="text-5xl font-bold text-sketch-red leading-none flex-shrink-0" style={{ fontFamily: "var(--font-heading)" }}>{num}</div>
                <div>
                  <h3 className="text-sketch-blue mb-1">{title}</h3>
                  <p className="text-sketch-muted">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Profile Preview */}
      <section id="profile-preview" className="py-16 px-8 max-w-5xl mx-auto">
        <h2 className="text-center mb-10 rotate-[0.5deg]">Hồ sơ Năng lực Cá nhân</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div id="top-careers-preview" className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 -rotate-[1deg] pinned">
            <h3 className="flex items-center gap-2 mb-4 text-sketch-blue">
              <GraduationCap size={24} /> Top ngành phù hợp
            </h3>
            <div className="flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1.5 px-4 py-1.5 border-[2px] border-sketch-ink rounded-full bg-sketch-yellow shadow-sketch text-sm font-semibold">
                <Star size={14} /> Khoa học máy tính
              </span>
              <span className="inline-flex items-center gap-1.5 px-4 py-1.5 border-[2px] border-sketch-ink rounded-full bg-sketch-surface shadow-sketch text-sm font-semibold">
                <CheckCircle2 size={14} /> Phân tích dữ liệu kinh doanh
              </span>
              <span className="inline-flex items-center gap-1.5 px-4 py-1.5 border-[2px] border-sketch-ink rounded-full bg-sketch-surface shadow-sketch text-sm font-semibold">
                <CheckCircle2 size={14} /> Kỹ thuật phần mềm
              </span>
            </div>
          </div>
          <div id="prediction-preview" className="relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 rotate-[1deg] pinned">
            <h3 className="flex items-center gap-2 mb-4 text-sketch-blue">
              <TrendingUp size={24} /> Dự đoán trúng tuyển
            </h3>
            <div className="space-y-2">
              {[
                { label: "ĐH Bách Khoa (IT1)", badge: "Thách thức", bg: "bg-red-50", text: "text-red-800" },
                { label: "ĐH Kinh tế Quốc dân", badge: "Cân bằng", bg: "bg-blue-50", text: "text-sketch-blue" },
                { label: "ĐH FPT (SE)", badge: "An toàn", bg: "bg-green-50", text: "text-green-800" },
              ].map(({ label, badge, bg, text }) => (
                <div key={label} className="flex items-center justify-between px-4 py-2 border-[2px] border-sketch-ink rounded-xl bg-sketch-surface">
                  <span className="font-bold" style={{ fontFamily: "var(--font-heading)" }}>{label}</span>
                  <span className={`text-sm px-3 py-0.5 rounded-full border-[2px] border-sketch-ink font-bold ${bg} ${text}`}>{badge}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <hr className="hand-drawn-hr" />

      {/* AI Tech */}
      <section id="ai-tech" className="py-16 px-8 max-w-5xl mx-auto">
        <h2 className="text-center mb-10 -rotate-[0.5deg]">Công nghệ đằng sau</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { id: "tech-1", icon: <Bot size={40} strokeWidth={1.5} />, title: "LLM Engine", desc: "Xử lý ngôn ngữ tự nhiên để tư vấn như một chuyên gia thực thụ.", rotate: "rotate-[1deg]" },
            { id: "tech-2", icon: <Radio size={40} strokeWidth={1.5} />, title: "Machine Learning", desc: "Học hỏi từ xu hướng nghề nghiệp và dữ liệu thị trường liên tục.", rotate: "-rotate-[1deg]" },
            { id: "tech-3", icon: <Database size={40} strokeWidth={1.5} />, title: "RAG Architecture", desc: "Kết nối trực tiếp với cơ sở dữ liệu tuyển sinh chính thức.", rotate: "rotate-[1deg]" },
          ].map(({ id, icon, title, desc, rotate }) => (
            <div key={id} id={id} className={`bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 text-center transition-all duration-200 hover:-translate-y-1 ${rotate}`}>
              <div className="flex justify-center mb-2 text-sketch-blue">{icon}</div>
              <h4 className="text-sketch-blue mb-2" style={{ fontFamily: "var(--font-heading)", fontSize: 18 }}>{title}</h4>
              <p className="text-sketch-muted text-base">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits */}
      <section id="benefits" className="section-alt-bg py-16 px-8">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-center mb-10">Dành cho tất cả mọi người</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { id: "benefit-student", icon: <Backpack size={24} />, title: "Cho Học Sinh", rotate: "-rotate-[1deg]", items: ["Tự tin với lựa chọn của mình", "Giảm áp lực thi cử vô định", "Khám phá tiềm năng ẩn giấu"] },
              { id: "benefit-parent", icon: <Users size={24} />, title: "Cho Phụ Huynh", rotate: "rotate-[1deg]", items: ["Đồng hành cùng con dựa trên cơ sở khoa học", "Tối ưu hóa chi phí đầu tư giáo dục", "Giảm bớt mâu thuẫn gia đình"] },
              { id: "benefit-school", icon: <School size={24} />, title: "Cho Nhà Trường", rotate: "-rotate-[1deg]", items: ["Tăng tỉ lệ học sinh đỗ nguyện vọng 1", "Công cụ hướng nghiệp hiện đại", "Quản lý năng lực học sinh dễ dàng"] },
            ].map(({ id, icon, title, rotate, items }) => (
              <div key={id} id={id} className={`relative bg-sketch-surface border-[2px] border-sketch-ink wobbly shadow-sketch-md p-6 tape ${rotate}`}>
                <h3 className="flex items-center gap-2 mb-4 text-sketch-red">{icon} {title}</h3>
                <ul className="benefit-list space-y-2.5 list-none">
                  {items.map((item) => <li key={item} className="flex items-center text-lg">{item}</li>)}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section id="cta-banner" className="text-center py-16 px-8 bg-sketch-ink">
        <h2 className="text-sketch-yellow mb-3">Bắt đầu hành trình của bạn</h2>
        <p className="text-sketch-surface-dim text-xl mb-8">
          Gia nhập cùng <span className="text-sketch-yellow font-bold">50.000+</span> học sinh đã tìm thấy con đường của mình qua SketchApp AI.
        </p>
        <Link
          href="/signup"
          id="cta-signup-btn"
          className="inline-flex items-center gap-2 px-10 py-4 text-white font-bold border-[2px] border-sketch-yellow bg-sketch-red wobbly-btn shadow-sketch-red text-xl hover:no-underline transition-all active:shadow-pressed active:translate-x-1 active:translate-y-1"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          <Pencil size={20} /> Đăng ký miễn phí
        </Link>
      </section>

      <Footer />
    </>
  );
}
