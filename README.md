# 🚀 Sketch App - Backend Microservices Monorepo

Chào mừng bạn đến với hệ thống Backend của **Sketch App** (Tích hợp AI dự đoán tuyển sinh & RAG Chatbot). Dự án này được thiết kế theo kiến trúc **Microservices** chạy trên Docker, sử dụng FastAPI và PostgreSQL.

File tài liệu này sẽ hướng dẫn bạn cách thiết lập môi trường, hiểu rõ cấu trúc thư mục và quy trình phát triển.

---

## 🛠️ Tech Stack
*   **Framework:** FastAPI (Python 3.11+)
*   **Database:** PostgreSQL 16
*   **ORM & Migration:** SQLAlchemy 2.0 & Alembic
*   **Authentication:** JWT (JSON Web Token) & Bcrypt
*   **Infrastructure:** Docker & Docker Compose
*   **Architecture:** Microservices, API Gateway, Clean Architecture

---

## 📂 Cấu trúc thư mục (Monorepo)

Dự án áp dụng mô hình Monorepo (chứa nhiều services trong một repo). Cấu trúc tổng thể như sau:

```text
backend/
├── api_gateway/              # Trạm trung chuyển (Reverse Proxy), điều hướng request từ Frontend
│   └── app/                  # Chứa logic định tuyến tới các services bằng httpx
├── services/                 # Nơi chứa các Microservices độc lập
│   ├── admission_service/    # AI dự đoán điểm chuẩn (XGBoost/LightGBM)
│   ├── profile_service/      # Quản lý User, Authentication (Login/Register), JWT
│   ├── rag_service/          # Hệ thống Chatbot RAG xử lý tài liệu
│   └── riasec_service/       # Hệ thống bài test định hướng nghề nghiệp Holland
├── .env.example              # File mẫu chứa các biến môi trường
├── docker-compose.yml        # Cấu hình khởi chạy toàn bộ hệ thống Docker
└── README.md                 # Tài liệu bạn đang đọc
```

### 🔍 Clean Architecture trong mỗi Service
Mỗi service đều tuân thủ chặt chẽ Clean Architecture để dễ bảo trì và mở rộng:
*   `app/api/`: Chứa các Router/Endpoints (Controller).
*   `app/services/`: Chứa logic nghiệp vụ lõi (Business Logic).
*   `app/repositories/`: Xử lý giao tiếp trực tiếp với Database (CRUD).
*   `app/models/`: Định nghĩa các bảng Database (SQLAlchemy).
*   `app/schemas/`: Định nghĩa dữ liệu đầu vào/đầu ra (Pydantic / DTOs).
*   `app/core/`: Cấu hình hệ thống, Database config, Security.

---

## ⚙️ Hướng dẫn cài đặt cho người mới (Getting Started)

### Bước 1: Yêu cầu hệ thống
Hãy chắc chắn máy tính của bạn đã cài đặt:
1.  **Git**
2.  **Docker** và **Docker Compose** (Khuyến nghị cài đặt Docker Desktop).

### Bước 2: Clone dự án và cấu hình biến môi trường
```bash
git clone <url-repo-cua-ban>
cd backend
```
Tạo một file `.env` ở thư mục gốc (copy từ file `.env.example` nếu có) và cấu hình các biến cơ bản:
```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_DB=sketch_db
POSTGRES_PORT=5432
JWT_SECRET=chuoi-bao-mat-cua-ban-o-day
```

### Bước 3: Khởi chạy toàn bộ hệ thống bằng Docker
Chỉ với 1 dòng lệnh, Docker sẽ tự động tải các image, cài đặt thư viện và chạy database:
```bash
docker-compose up -d --build
```
*(Cờ `-d` giúp chạy ngầm, `--build` để đảm bảo nhận code mới nhất).*

### Bước 4: Chạy Migration để tạo cấu trúc Database ban đầu
Hiện tại hệ thống đã cấu hình Alembic. Chạy lệnh sau để tự động tạo các bảng (như bảng `users`) trong PostgreSQL:
```bash
docker exec -it ms_profile_service alembic upgrade head
```

---

## 🧪 Hướng dẫn Test API (Swagger UI)

Hệ thống cung cấp sẵn tài liệu API trực quan. Vì sử dụng Microservices, chúng ta mở các cổng giao tiếp khác nhau để Developer dễ dàng test độc lập:

| Dịch vụ | Cổng (Port) | Đường dẫn Swagger UI | Chức năng |
| :--- | :--- | :--- | :--- |
| **API Gateway** | `8000` | [http://localhost:8000/docs](http://localhost:8000/docs) | Cổng chính. Frontend chỉ gọi vào đây. Không dùng để test logic nội bộ. |
| **Profile Service** | `8001` | [http://localhost:8001/docs](http://localhost:8001/docs) | Dùng để test API Đăng ký, Đăng nhập, Profile. |
| **RIASEC Service** | `8002` | [http://localhost:8002/docs](http://localhost:8002/docs) | Dùng để test API bài test nghề nghiệp. |
| **Admission Service**| `8003` | [http://localhost:8003/docs](http://localhost:8003/docs) | Dùng để test API dự đoán điểm chuẩn (AI). |
| **RAG Service** | `8004` | [http://localhost:8004/docs](http://localhost:8004/docs) | Dùng để test API Chatbot RAG. |

**💡 Mẹo test Đăng nhập (Auth):**
Để test các API yêu cầu đăng nhập (ví dụ: `GET /api/profile/me`), hãy mở Swagger của `Profile Service` (Port 8001), nhấn vào nút **Authorize** (biểu tượng ổ khóa) ở góc trên bên phải, nhập Email và Mật khẩu. Swagger sẽ tự động lưu Token cho các request tiếp theo.

---

## 👨‍💻 Quy trình Code (Development Workflow)

1.  **Auto Reload Code:** 
    Các container đã được gắn Volume. Khi bạn sửa code Python và bấm lưu, Uvicorn trong Docker sẽ **tự động reload** ngay lập tức. Bạn không cần phải restart lại container.
    
2.  **Thêm thư viện mới (Cực kỳ quan trọng):** 
    Nếu bạn cài thêm package và thêm vào file `requirements.txt` trong bất kỳ service nào, bạn **bắt buộc** phải build lại riêng service đó để Docker tải thư viện:
    ```bash
    docker-compose up -d --build <ten_service>
    # Ví dụ: docker-compose up -d --build admission_service
    ```
    
3.  **Tạo/Sửa bảng Database:** 
    Khi bạn tạo hoặc sửa một model trong thư mục `models/` của profile_service, hãy chạy 2 lệnh sau để cập nhật Database:
    ```bash
    # 1. Tạo file migration tự động phát hiện thay đổi
    docker exec -it ms_profile_service alembic revision --autogenerate -m "Mô tả thay đổi của bạn"
    
    # 2. Áp dụng thay đổi vào Database
    docker exec -it ms_profile_service alembic upgrade head
    ```

---
*Chúc team code vui vẻ và hệ thống luôn chạy mượt mà! 🚀*