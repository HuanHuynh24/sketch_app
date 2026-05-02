# 🎓 AI Admission System

Hệ thống Tư vấn Hướng nghiệp và Dự đoán Điểm chuẩn Đại học năm 2026. Dự án được thiết kế theo mô hình Monorepo, kết hợp sức mạnh của AI/LLM và Machine Learning để hỗ trợ học sinh THPT chọn ngành, chọn trường phù hợp.

## 🏗️ Kiến trúc Hệ thống

Dự án áp dụng triết lý Clean Architecture cho Backend và Atomic Design cho UI/UX, phân tách rõ ràng thành 2 phân hệ chính:

### 1. Frontend (`/frontend`)
- **Công nghệ:** Next.js, React, Tailwind CSS.
- **Vai trò:** Cung cấp giao diện tương tác mượt mà cho học sinh (Chatbot hướng nghiệp, Form nhập điểm dự đoán).

### 2. Backend (`/backend`)
Hệ thống Microservices được viết bằng **Python (FastAPI)** và quản lý tập trung qua **Docker**. Bao gồm các services:
- 🚪 **API Gateway:** Cổng giao tiếp duy nhất, điều phối request và kiểm tra bảo mật (CORS, Rate Limiting).
- 👤 **Profile Service:** Quản lý thông tin học sinh, phân quyền và xác thực bằng JWT.
- 🧠 **RIASEC Service (Phân hệ 1):** Tích hợp AI Agent (Gemini/OpenAI qua LangChain) để đóng vai chuyên gia tư vấn hướng nghiệp, phân tích nhóm tính cách theo chuẩn RIASEC.
- 📊 **Admission Service (Phân hệ 2):** Sử dụng các mô hình Machine Learning (XGBoost, LightGBM) để dự đoán khả năng trúng tuyển dựa trên điểm khối thi.
- 📚 **RAG Service (Phân hệ 3):** Trợ lý AI đọc hiểu Đề án tuyển sinh (PDF) kết hợp Vector Database (ChromaDB) để trả lời thắc mắc chuẩn xác.

## 🚀 Hướng dẫn Cài đặt & Vận hành

Yêu cầu môi trường: Cài đặt sẵn `Node.js`, `Docker` và `Docker Compose` (Ưu tiên chạy trên môi trường Linux/WSL).

### Bật Backend (Microservices)
Di chuyển vào thư mục backend và khởi động các container:
```bash
cd backend
docker-compose up -d --build