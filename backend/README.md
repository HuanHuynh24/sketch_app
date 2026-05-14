# Sketch App Backend

Backend cho hệ thống tư vấn tuyển sinh và định hướng nghề nghiệp. Dự án được tổ chức theo kiến trúc Microservices, mỗi service phụ trách một nhóm nghiệp vụ riêng và dùng chung PostgreSQL nhưng tách schema theo service.

## 1. Mục tiêu dự án

Hệ thống hỗ trợ học sinh:

- Đăng ký và quản lý hồ sơ cá nhân.
- Làm bài đánh giá định hướng nghề nghiệp RIASEC.
- Nhận kết quả phân tích theo mã Holland RIASEC.
- Nhận gợi ý nhóm ngành, ngành học, vai trò nghề nghiệp và kỹ năng nên phát triển.
- Tra cứu thông tin tuyển sinh và tư vấn thông qua các service mở rộng.

## 2. Kiến trúc tổng quan

```txt
Frontend
   |
   v
API Gateway :8000
   |
   +--------------------+
   |                    |
   v                    v
Profile Service       RIASEC Service
:8001                 :8002
   |                    |
   +---------+----------+
             |
             v
        PostgreSQL

Các service hiện có:

backend/
├── api_gateway/
├── services/
│   ├── profile_service/
│   ├── riasec_service/
│   ├── admission_service/
│   └── rag_service/
├── docker-compose.yml
├── .env
└── README.md
3. Công nghệ sử dụng
FastAPI
PostgreSQL 16
SQLAlchemy
Alembic
Docker Compose
Pydantic
Gemini API
Microservices Architecture
4. Danh sách service
4.1. Profile Service

Phụ trách quản lý học sinh.

Base URL local:

http://localhost:8001/api/profile

Swagger:

http://localhost:8001/docs

Chức năng chính:

Đăng ký học sinh.
Đăng nhập.
Lấy thông tin học sinh hiện tại.
Quản lý hồ sơ học sinh.

Schema DB:

profile
4.2. RIASEC Service

Phụ trách bài đánh giá định hướng nghề nghiệp theo Holland RIASEC.

Base URL local:

http://localhost:8002/api/riasec

Swagger:

http://localhost:8002/docs

Chức năng chính:

Tạo phiên đánh giá RIASEC.
Sinh câu hỏi tình huống bằng Gemini.
Chấm điểm câu trả lời theo 6 nhóm R-I-A-S-E-C.
Tự động chọn câu hỏi tiếp theo dựa trên điểm số hiện tại.
Kiểm tra câu trả lời không nghiêm túc hoặc lạc đề.
Chống lặp câu hỏi.
Giới hạn tối đa 7 câu hỏi hợp lệ.
Tạo kết quả cuối gồm:
Mã RIASEC.
Điểm từng nhóm.
Độ tin cậy.
Nhóm ngành phù hợp.
Ngành học gợi ý.
Năng lực số nên phát triển.
Báo cáo tổng hợp.

Schema DB:

riasec
4.3. Admission Service

Phụ trách nghiệp vụ tuyển sinh.

Base URL local:

http://localhost:8003/api/admission

Swagger:

http://localhost:8003/docs

Schema DB:

admission
4.4. RAG Service

Phụ trách truy xuất thông tin và hỏi đáp bằng RAG.

Base URL local:

http://localhost:8004/api/rag

Swagger:

http://localhost:8004/docs

Schema DB:

rag
5. Cấu hình môi trường

Tạo file .env tại thư mục backend/.

Ví dụ:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sketch_db
POSTGRES_PORT=5432

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash

Không commit .env lên Git.

Đảm bảo .gitignore có:

.env
__pycache__/
*.pyc
.venv/
6. Chạy project

Tại thư mục:

D:\sketch_app\backend

Chạy toàn bộ hệ thống:

docker compose up -d --build

Chạy riêng từng service:

docker compose up -d --build profile_service
docker compose up -d --build riasec_service
docker compose up -d --build admission_service
docker compose up -d --build rag_service

Kiểm tra container:

docker ps

Xem log:

docker logs -f ms_profile_service
docker logs -f ms_riasec_service
docker logs -f ms_admission_service
docker logs -f ms_rag_service
7. Health check
curl http://localhost:8001/api/profile/health
curl http://localhost:8002/api/riasec/health
curl http://localhost:8003/api/admission/health
curl http://localhost:8004/api/rag/health
8. Migration database

Mỗi service dùng Alembic riêng và schema riêng.

Ví dụ chạy migration cho riasec_service:

docker exec -it ms_riasec_service alembic revision --autogenerate -m "init_riasec_service"
docker exec -it ms_riasec_service alembic upgrade head

Ví dụ chạy migration cho profile_service:

docker exec -it ms_profile_service alembic revision --autogenerate -m "init_profile_service"
docker exec -it ms_profile_service alembic upgrade head

Kiểm tra bảng trong PostgreSQL:

docker exec -it ms_postgres psql -U postgres -d sketch_db

Trong psql:

\dt profile.*
\dt riasec.*
\dt admission.*
\dt rag.*
9. Luồng test nhanh RIASEC
Bước 1: Đăng ký học sinh
POST http://localhost:8001/api/profile/auth/register

Body:

{
  "full_name": "Nguyen Van Test",
  "email": "test_riasec@example.com",
  "password": "123456",
  "province": "Khánh Hòa",
  "area_code": "KV2",
  "dob": "2007-05-20",
  "priority_group": "01",
  "target_province": "TP.HCM"
}

Lấy student_id từ response.

Bước 2: Tạo phiên RIASEC
POST http://localhost:8002/api/riasec/sessions

Body:

{
  "student_id": "UUID_STUDENT"
}

Lấy session_id từ response.

Bước 3: Gửi câu trả lời
POST http://localhost:8002/api/riasec/sessions/{session_id}/answers

Body:

{
  "answer_text": "Em thích phân tích dữ liệu, tìm xu hướng và đề xuất giải pháp phù hợp."
}

Sau tối đa 7 câu trả lời hợp lệ, hệ thống trả về status = completed và dcp_id.

Bước 4: Lấy kết quả cuối
GET http://localhost:8002/api/riasec/profiles/{dcp_id}
10. Quy ước Git

Kiểm tra thay đổi:

git status

Commit gợi ý:

git add .
git commit -m "feat(riasec): improve adaptive testing and career report"
git push origin main
11. Lưu ý cho thành viên mới
Không commit .env.
Không query trực tiếp schema của service khác trong code service.
Service gọi nhau bằng internal URL trong Docker network, ví dụ:
http://profile_service:8000
http://riasec_service:8000
Không dùng localhost khi service gọi service trong Docker.
Khi thêm bảng mới cần tạo migration Alembic.
Khi thêm biến môi trường mới cần cập nhật:
.env
docker-compose.yml
app/core/config.py