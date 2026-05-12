# SKILL — Sketch App Backend (AI Admission Counseling Platform)

## 1. Tổng Quan Dự Án

Hệ thống **tư vấn tuyển sinh đại học** sử dụng AI, được xây dựng theo kiến trúc **Microservices** với Python/FastAPI. Hệ thống bao gồm:

- Trắc nghiệm hướng nghiệp RIASEC (Holland Code) qua hội thoại AI
- Dự đoán điểm chuẩn tuyển sinh bằng Machine Learning (XGBoost)
- Chatbot RAG (Retrieval-Augmented Generation) tư vấn tuyển sinh
- Quản lý hồ sơ người dùng (học sinh THPT Việt Nam)

**Tech Stack chính:**
- **Language:** Python 3.11
- **Framework:** FastAPI 0.110.0
- **ORM:** SQLAlchemy 2.0.29 (sync sessions)
- **Database:** PostgreSQL 16 (shared instance, mỗi service dùng bảng riêng)
- **Migration:** Alembic 1.13.1 (mỗi service có `alembic_version_<service_name>` table riêng)
- **Auth:** JWT (HS256) — `python-jose` (profile_service), `PyJWT` (riasec_service, gateway)
- **AI/LLM:** Google Gemini 1.5 Flash (`google-generativeai`)
- **ML:** XGBoost, scikit-learn, pandas
- **RAG:** LangChain, FAISS, tiktoken, pdfplumber
- **Container:** Docker Compose, Python 3.11-slim base image
- **Server:** Uvicorn với `--reload` (dev mode)

---

## 2. Kiến Trúc Hệ Thống

```
Frontend (port 8000)
    │
    ▼
┌─────────────────────────────────────────┐
│         API Gateway (port 8000)         │  ← Reverse proxy, CORS, JWT verify
│         ms_api_gateway                  │
└───┬──────────┬──────────┬──────────┬────┘
    │          │          │          │
    ▼          ▼          ▼          ▼
 Profile    RIASEC    Admission    RAG
 :8001      :8002      :8003      :8004
```

### Docker Network: `ai_admission_network`
- Tất cả services giao tiếp nội bộ qua container name (VD: `http://ms_profile_service:8000`)
- Shared database: `ms_postgres` (PostgreSQL 16)
- Shared database name: `sketch_db`

### Port Mapping

| Service           | Container Name        | Internal Port | External Port |
|-------------------|-----------------------|---------------|---------------|
| PostgreSQL        | ms_postgres           | 5432          | 5432          |
| Profile Service   | ms_profile_service    | 8000          | 8001          |
| RIASEC Service    | ms_riasec_service     | 8000          | 8002          |
| Admission Service | ms_admission_service  | 8000          | 8003          |
| RAG Service       | ms_rag_service        | 8000          | 8004          |
| API Gateway       | ms_api_gateway        | 8000          | 8000          |

---

## 3. Cấu Trúc Thư Mục

```
backend/
├── .env                          # Biến môi trường chung (DB, JWT, GEMINI_API_KEY)
├── docker-compose.yml            # Orchestration cho tất cả services
├── make_service.sh               # Script tạo service mới từ template
├── RIASEC.md                     # Tài liệu 60 câu hỏi RIASEC
├── SKILL.md                      # File này
│
├── api_gateway/                  # Reverse proxy gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               # FastAPI app, include 4 routers
│       ├── core/
│       │   ├── config.py         # Settings: JWT + service URLs
│       │   └── security.py       # verify_token() — JWT decode
│       ├── routes/               # Proxy routes (forward via httpx)
│       │   ├── profile.py        # → ms_profile_service/api/profile/
│       │   ├── riasec.py         # → ms_riasec_service/api/riasec/
│       │   ├── admission.py      # → ms_admission_service/api/admission/
│       │   └── rag.py            # → ms_rag_service/api/rag/
│       └── utils/
│           └── http_client.py    # forward_request() helper (timeout 10s)
│
└── services/
    ├── _template_service/        # Bản mẫu cho service mới
    │
    ├── profile_service/          # Quản lý user, auth (JWT)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── alembic/              # Migration
    │   ├── alembic.ini
    │   ├── API_DOCS.md           # Tài liệu API
    │   └── app/
    │       ├── main.py
    │       ├── core/
    │       │   ├── config.py     # Settings (pydantic_settings)
    │       │   ├── database.py   # engine, SessionLocal, get_db()
    │       │   └── security.py   # pwd hash (bcrypt), JWT create
    │       ├── models/
    │       │   ├── base.py       # declarative_base()
    │       │   └── user.py       # User model (bảng `users`)
    │       ├── schemas/
    │       │   └── user.py       # UserCreate, UserResponse, UserLogin, Token
    │       ├── repositories/
    │       │   └── user_repo.py  # UserRepository (get_by_email, create)
    │       ├── services/
    │       │   └── user_service.py # UserService (create_user, authenticate)
    │       └── api/
    │           ├── deps.py       # get_current_user() dependency
    │           ├── health.py     # GET /health
    │           └── users_router.py # POST register, login, GET /me
    │
    ├── riasec_service/           # Trắc nghiệm RIASEC qua hội thoại AI
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── alembic/
    │   ├── alembic.ini
    │   └── app/
    │       ├── main.py
    │       ├── core/
    │       │   ├── config.py     # Settings + GEMINI_API_KEY
    │       │   ├── database.py   # engine, SessionLocal, get_db()
    │       │   └── security.py   # get_current_user_id() (đang mock)
    │       ├── models/
    │       │   ├── base.py
    │       │   ├── riasec_session.py        # RiasecSession
    │       │   ├── conversation_message.py  # ConversationMessage
    │       │   └── universities_majors.py   # UniversitiesMajors
    │       ├── schemas/
    │       │   └── riasec.py     # Session/Message Create/Response schemas
    │       ├── repositories/     # (trống — query trực tiếp trong endpoint)
    │       ├── services/
    │       │   ├── llm_service.py      # Gemini: generate_question, extract_signal, final_scoring
    │       │   └── scoring_service.py  # calc_confidence, should_stop, run_final_scoring_job
    │       └── api/
    │           ├── endpoints/
    │           │   └── riasec.py # CRUD sessions + send_message
    │           └── health.py
    │
    ├── admission_service/        # Dự đoán điểm tuyển sinh (XGBoost)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── core/             # config, database, security
    │       ├── models/           # base, history
    │       ├── schemas/          # predict_schema
    │       ├── repositories/     # history_repo
    │       ├── services/
    │       │   ├── ai_predictor.py    # XGBoost model load + predict
    │       │   └── history_service.py
    │       └── api/
    │           ├── health.py
    │           └── predict_router.py
    │
    └── rag_service/              # Chatbot RAG (chưa implement)
        ├── Dockerfile
        ├── requirements.txt
        └── app/
            ├── main.py
            ├── core/             # config, database, security
            ├── models/           # base only
            ├── schemas/          # (trống)
            ├── repositories/     # (trống)
            ├── services/         # (trống)
            └── api/
                └── health.py
```

---

## 4. Models (SQLAlchemy ORM)

### 4.1 Profile Service — `users` table

```python
class User(Base):
    __tablename__ = "users"
    # PK
    student_id       UUID(as_uuid=True)  PK, default=uuid4
    # Thông tin cá nhân
    full_name        String(100)         NOT NULL
    email            String(200)         NOT NULL, UNIQUE
    password_hash    String(255)         NOT NULL        # bcrypt hash
    dob              Date                nullable
    province         String(100)         NOT NULL
    area_code        String(5)           NOT NULL        # KV1/KV2/KV3
    priority_group   String(10)          nullable        # 01–07
    target_province  String(100)         nullable
    is_active        Boolean             default=True
    # Kết quả học tập
    grade_10_avg     Float               nullable
    grade_11_avg     Float               nullable
    grade_12_avg     Float               nullable
    exam_scores      JSONB               nullable        # {toan, van, anh, ly, hoa, sinh...}
    exam_type        String(20)          nullable        # thpt | dgnl | dgtd
    exam_year        Integer             nullable
    # Kết quả RIASEC (được cập nhật bởi riasec_service background job)
    score_R          Float               nullable        # 0–100
    score_I          Float               nullable
    score_A          Float               nullable
    score_S          Float               nullable
    score_E          Float               nullable
    score_C          Float               nullable
    riasec_code      String(3)           nullable        # VD: "RIA"
    top_groups       ARRAY(String)       nullable        # ['R','I']
    confidence       Float               nullable        # 0.0–1.0
    reasoning        Text                nullable        # AI reasoning
    suggested_majors JSONB               nullable        # [{group, majors, fit_reason}]
    created_at       TIMESTAMP(tz)       nullable
    updated_at       TIMESTAMP(tz)       nullable
```

### 4.2 RIASEC Service — `riasec_sessions` table

```python
class RiasecSession(Base):
    __tablename__ = "riasec_sessions"
    session_id       UUID(as_uuid=True)  PK, default=uuid4
    student_id       String              NOT NULL, INDEX
    status           String(20)          NOT NULL, default="in_progress"  # in_progress|completed|abandoned
    question_count   Integer             default=0
    current_scores   JSONB               default={}     # {"R":0,"I":0,"A":0,"S":0,"E":0,"C":0}
    confidence       Float               default=0.0
    groups_asked     JSONB               default={}     # Đếm số lần hỏi mỗi nhóm
    started_at       DateTime            default=utcnow
    completed_at     DateTime            nullable
```

### 4.3 RIASEC Service — `conversation_messages` table

```python
class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    message_id       UUID(as_uuid=True)  PK, default=uuid4
    session_id       UUID(as_uuid=True)  FK → riasec_sessions.session_id (CASCADE)
    role             String(10)          NOT NULL        # "user" | "assistant"
    content          Text                NOT NULL
    riasec_target    String(3)           nullable        # Nhóm RIASEC mục tiêu
    sequence_no      Integer             NOT NULL        # Thứ tự tin nhắn
    created_at       DateTime            default=utcnow
```

### 4.4 RIASEC Service — `universities_majors` table

```python
class UniversitiesMajors(Base):
    __tablename__ = "universities_majors"
    id                  UUID(as_uuid=True)  PK, default=uuid4
    student_id          String(200)         NOT NULL, INDEX
    logo                String(50)          NOT NULL
    content             Text                NOT NULL
    type                Integer             NOT NULL, default=0
    name_universities   String(20)          NOT NULL
    name_majors         String(200)         nullable
    updated_at          DateTime            default=utcnow, onupdate=utcnow
```

---

## 5. Schemas (Pydantic)

### 5.1 Profile Service

```python
class UserCreate(BaseModel):       # Request — đăng ký
    email: str
    password: str                   # min_length=6, max_length=50
    full_name: str

class UserResponse(BaseModel):     # Response — trả về (giấu password)
    id: int
    email: str
    full_name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):        # Request — đăng nhập
    email: str
    password: str                   # max_length=50

class Token(BaseModel):            # Response — JWT token
    access_token: str
    token_type: str = "bearer"
```

### 5.2 RIASEC Service

```python
class SessionCreate(BaseModel):          # Request — tạo session
    student_id: str

class SessionResponse(BaseModel):       # Response — thông tin session
    session_id: str
    first_question: Optional[str]
    question_no: Optional[int]
    status: Optional[str]
    question_count: Optional[int]
    confidence: Optional[float]

class MessageCreate(BaseModel):          # Request — gửi câu trả lời
    answer: str                          # max_length=2000

class MessageResponse(BaseModel):       # Response — câu hỏi tiếp
    status: str                          # "in_progress" | "completed"
    next_question: Optional[str]
    question_no: Optional[int]
    confidence: Optional[float]

class SessionAbandonResponse(BaseModel): # Response — bỏ session
    session_id: str
    status: str
```

---

## 6. API Endpoints

### 6.1 API Gateway (port 8000) — Reverse Proxy

| Prefix             | Target Service                              |
|---------------------|---------------------------------------------|
| `/api/profile/{p}`  | `http://ms_profile_service:8000/api/profile/{p}` |
| `/api/riasec/{p}`   | `http://ms_riasec_service:8000/api/riasec/{p}`   |
| `/api/admission/{p}`| `http://ms_admission_service:8000/api/admission/{p}` |
| `/api/rag/{p}`      | `http://ms_rag_service:8000/api/rag/{p}`     |
| `GET /health`       | Gateway health check                         |

### 6.2 Profile Service (port 8001)

| Method | Path                    | Auth | Mô tả                |
|--------|-------------------------|------|-----------------------|
| POST   | /api/profile/register   | ✗    | Đăng ký user mới      |
| POST   | /api/profile/login      | ✗    | Đăng nhập (OAuth2 form) |
| GET    | /api/profile/me         | ✔    | Lấy thông tin user     |
| GET    | /health                 | ✗    | Health check           |

### 6.3 RIASEC Service (port 8002)

| Method | Path                                      | Auth   | Mô tả                    |
|--------|--------------------------------------------|--------|---------------------------|
| POST   | /api/v1/riasec/sessions                   | mock   | Tạo session mới + câu hỏi đầu |
| POST   | /api/v1/riasec/sessions/{id}/messages     | mock   | Gửi trả lời, nhận câu hỏi tiếp |
| GET    | /api/v1/riasec/sessions/{id}              | mock   | Xem trạng thái session    |
| PATCH  | /api/v1/riasec/sessions/{id}/abandon      | mock   | Bỏ session                |
| GET    | /health                                    | ✗      | Health check              |

> **Lưu ý:** RIASEC service prefix là `/api/v1/riasec` (có v1), khác với gateway prefix `/api/riasec`.

### 6.4 Admission Service (port 8003)

| Method | Path                    | Auth | Mô tả                |
|--------|-------------------------|------|-----------------------|
| POST   | /api/admission/predict  | —    | Dự đoán điểm chuẩn   |
| GET    | /health                 | ✗    | Health check           |

---

## 7. Luồng Xử Lý RIASEC (Core Business Flow)

```
1. Client → POST /sessions {student_id}
   → Tạo RiasecSession (status=in_progress, question_count=1)
   → Gọi Gemini generate_question(câu 1, no history)
   → Lưu ConversationMessage (role=assistant)
   → Trả về {session_id, first_question, question_no=1}

2. Client → POST /sessions/{id}/messages {answer}
   → Lưu ConversationMessage (role=user)
   → Gọi Gemini extract_signal(answer) → {"R":+2, "I":+1, ...}
   → Cộng dồn vào session.current_scores
   → calc_confidence() → confidence score
   → should_stop()? → Nếu đúng:
       → session.status = "completed"
       → BackgroundTasks → run_final_scoring_job()
           → Gemini phân tích toàn bộ hội thoại
           → UPDATE users SET score_R, riasec_code, reasoning, suggested_majors...
       → Trả {status: "completed"}
   → Nếu chưa stop:
       → Gọi Gemini generate_question(câu tiếp, target_groups, saturated, history)
       → Lưu ConversationMessage (role=assistant)
       → Trả {status: "in_progress", next_question, confidence}

Điều kiện dừng:
  - question_no >= 25 (hard limit)
  - confidence >= 0.80 AND gap >= 15 AND question_no >= 8
```

---

## 8. Coding Convention & Patterns

### 8.1 Kiến Trúc Clean Architecture (mỗi service)

```
app/
├── api/          # Layer 1: HTTP handlers (routers, endpoints, deps)
├── schemas/      # Layer 2: Pydantic DTOs (request/response validation)
├── services/     # Layer 3: Business logic
├── repositories/ # Layer 4: Data access (DB queries)
├── models/       # Layer 5: SQLAlchemy ORM models
└── core/         # Infrastructure: config, database, security
```

**Luồng dữ liệu:** `API → Schema (validate) → Service (logic) → Repository (query) → Model (ORM)`

### 8.2 Naming Convention

| Thành phần        | Convention                    | Ví dụ                          |
|-------------------|-------------------------------|--------------------------------|
| File              | snake_case                    | `user_service.py`              |
| Class             | PascalCase                    | `UserService`, `RiasecSession` |
| Function/Method   | snake_case                    | `create_user()`, `get_by_email()` |
| Variable          | snake_case                    | `student_id`, `current_scores` |
| Constant          | UPPER_SNAKE_CASE              | `JWT_SECRET`, `VERSION_TABLE`  |
| Table name        | snake_case (plural)           | `users`, `riasec_sessions`     |
| Column name       | snake_case                    | `full_name`, `score_R`         |
| Schema class      | PascalCase + suffix           | `UserCreate`, `SessionResponse`|
| Router file       | snake_case + `_router.py`     | `users_router.py`, `predict_router.py` |
| Service file      | snake_case + `_service.py`    | `user_service.py`, `llm_service.py` |
| Repo file         | snake_case + `_repo.py`       | `user_repo.py`                 |

### 8.3 Singleton Pattern cho Service/Repository

```python
# Cuối mỗi file service/repo, tạo instance singleton:
class UserService:
    def create_user(self, db: Session, user_in: UserCreate):
        ...

user_service = UserService()  # ← Singleton instance
```

### 8.4 Database Session Management

```python
# core/database.py — Giống nhau ở mọi service
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sử dụng trong endpoint:
@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    ...
```

### 8.5 Configuration Pattern

```python
# core/config.py — pydantic_settings cho services
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Service Name"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "fallback_url")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "fallback")
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# api_gateway dùng class thuần (không pydantic_settings)
class Settings:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "fallback")
    PROFILE_SERVICE_URL: str = os.getenv(..., "http://ms_profile_service:8000")
```

### 8.6 Authentication Pattern

**Profile Service:** Tạo JWT + verify JWT (dùng `python-jose`)
```python
# Tạo token
token = jwt.encode({"sub": user.email, "exp": expire}, JWT_SECRET, algorithm="HS256")

# Verify (dependency)
def get_current_user(credentials = Depends(HTTPBearer()), db = Depends(get_db)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    email = payload.get("sub")
    return user_repo.get_by_email(db, email)
```

**RIASEC Service:** Auth đang mock để test nhanh
```python
def get_current_user_id() -> str:
    return "test_user_id"  # Tắt auth để test
```

**API Gateway:** Verify JWT rồi forward request
```python
def verify_token(credentials = Security(HTTPBearer())):
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    return payload
```

### 8.7 Gateway Proxy Pattern

```python
# Mỗi route file trong gateway đều dùng pattern giống nhau:
@router.api_route("/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH"])
async def forward_request(path: str, request: Request):
    url = f"{settings.SERVICE_URL}/api/prefix/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)  # BẮT BUỘC xóa host header cho Docker
    async with httpx.AsyncClient() as client:
        response = await client.request(method=..., url=url, headers=headers,
                                        params=..., content=await request.body())
        return Response(content=response.content, status_code=response.status_code,
                       headers=dict(response.headers))
```

### 8.8 Alembic Migration Pattern

- Mỗi service có `alembic/` và `alembic.ini` riêng
- Version table riêng: `alembic_version_<service_name>` (tránh conflict shared DB)
- `include_object()` filter: chỉ quản lý bảng thuộc service đó
- Load `.env` trong `alembic/env.py` để lấy `DATABASE_URL`

### 8.9 Model Base Pattern

```python
# models/base.py — Giống nhau mọi service
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# models/__init__.py — PHẢI import tất cả models vào đây
from .base import Base
from .user import User  # Alembic cần để autogenerate
```

### 8.10 Error Handling Convention

```python
# Dùng HTTPException với status code chuẩn REST:
raise HTTPException(status_code=400, detail="Mô tả lỗi bằng tiếng Việt")
raise HTTPException(status_code=401, detail="Token không hợp lệ")
raise HTTPException(status_code=404, detail="Session not found")
raise HTTPException(status_code=409, detail="Đã có session in_progress")
raise HTTPException(status_code=503, detail="Service unavailable")
```

### 8.11 Async Convention

- **Endpoints gọi LLM:** Dùng `async def` + `await` (riasec endpoints)
- **Endpoints CRUD thuần:** Dùng `def` (sync) — profile, admission
- **Background tasks:** Dùng `BackgroundTasks` của FastAPI cho final scoring job
- **LLM calls:** Dùng `generate_content_async()` của Gemini SDK

### 8.12 Comment Convention

- Comment bằng **tiếng Việt** cho business logic, giải thích flow
- Comment bằng tiếng Anh cho technical/standard code
- Docstring ngắn gọn (1 dòng) cho API endpoints

---

## 9. Tạo Service Mới

```bash
./make_service.sh ten_service_moi
```

Script sẽ:
1. Copy `_template_service/` → `services/ten_service_moi/`
2. Tạo venv + cài requirements
3. Chạy Alembic init migration

Sau đó cần:
- Thêm service vào `docker-compose.yml` (port mới)
- Thêm route proxy vào `api_gateway/app/routes/`
- Include router mới trong `api_gateway/app/main.py`

---

## 10. Lưu Ý Quan Trọng

1. **Shared Database:** Tất cả services dùng chung 1 PostgreSQL instance (`sketch_db`). Mỗi service quản lý bảng riêng qua Alembic version table riêng.

2. **Cross-service Data Access:** `riasec_service` cập nhật trực tiếp bảng `users` (thuộc profile_service) qua raw SQL trong `scoring_service.py`. Đây là pattern coupling — cần lưu ý khi refactor.

3. **JWT Library Mismatch:** Profile service dùng `python-jose`, RIASEC service và gateway dùng `PyJWT`. Token format tương thích nhưng API khác nhau.

4. **RIASEC Auth Mock:** `riasec_service/core/security.py` đang return hardcoded `"test_user_id"`. Code JWT thật đã có nhưng bị comment out.

5. **JSONB Column Update:** Khi update JSONB column trong SQLAlchemy, phải `.copy()` dict trước khi gán lại để trigger change detection:
   ```python
   session.current_scores = current_scores.copy()
   ```

6. **Gateway Prefix Mismatch:** RIASEC service internal prefix là `/api/v1/riasec` nhưng gateway forward tới `/api/riasec/` — cần kiểm tra lại mapping.

7. **CORS:** Chỉ gateway và riasec_service có CORS middleware (`allow_origins=["*"]`).

8. **Model vs Schema Mismatch (Profile):** User model dùng `student_id` (UUID) làm PK nhưng `UserResponse` schema trả về `id: int` — cần đồng bộ.
