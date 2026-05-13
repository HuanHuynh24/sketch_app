**Cổng điều phối:** API Gateway (`Port 8000`) | Profile Service (`Port 8001`) | RIASEC Service (`Port 8002`)

---

## 🔑 1. FILE MẪU CẤU HÌNH MÔI TRƯỜNG (`.env.example`)

Dưới đây là file cấu hình môi trường mẫu. Hãy copy nội dung này vào file `.env` ở thư mục gốc của backend và điền khóa API của bạn:

```env
# Cấu hình PostgreSQL Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=sketch_db
POSTGRES_PORT=5432

# Chuỗi bí mật ký Token JWT (Độ dài khuyến nghị tối thiểu 32 ký tự)
JWT_SECRET=your_super_secret_jwt_sign_key_here_123456

# Google Gemini API Key (Lấy tại https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSy_DUMMY_GEMINI_KEY_EX_1234567890

# Groq AI API Key (Lấy tại https://console.groq.com/keys)
GROQ_API_KEY=gsk_DUMMY_GROQ_KEY_EX_abc123XYZ_9876543210

# Bật bảo mật hệ thống
AUTH_ENABLED=true
```

---

## 👤 2. API DỊCH VỤ THÔNG TIN CÁ NHÂN (`profile_service`)
> **Base URL:** `http://localhost:8000/api/profile` (Thông qua API Gateway)  
> **Định dạng dữ liệu:** `application/json`

### 2.1 Đăng ký tài khoản Học sinh (`POST /register`)
Khởi tạo tài khoản mới cho học sinh THPT.

*   **URL:** `/register`
*   **Method:** `POST`
*   **Body (JSON):**
    ```json
    {
      "email": "student@gmail.com",
      "password": "mypassword123",
    }
    ```
*   **Response Thành công (`201 Created`):**
    ```json
    {
      "student_id": "82f41586-7a24-49de-8fab-9f2e0df0dfa9",
      "email": "student@gmail.com",
      "full_name": "Nguyễn Văn A",
      "is_active": true
    }
    ```

### 2.2 Đăng nhập nhận Token JWT (`POST /login`)
Xác thực email/password và trả về JWT Token.

*   **URL:** `/login`
*   **Method:** `POST`
*   **Body (JSON):**
    ```json
    {
      "email": "student@gmail.com",
      "password": "mypassword123"
    }
    ```
*   **Response Thành công (`200 OK`):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "student_id": "82f41586-7a24-49de-8fab-9f2e0df0dfa9",
        "email": "student@gmail.com",
        "full_name": "Nguyễn Văn A",
        "is_active": true
      }
    }
    ```

### 2.3 Xem Hồ sơ Cá nhân & Điểm số (`GET /me`)
Lấy thông tin cá nhân hiện tại bao gồm cả điểm số RIASEC tích lũy.

*   **URL:** `/me`
*   **Method:** `GET`
*   **Authentication Required:** `Bearer <JWT_TOKEN>` trong Header.
*   **Response Thành công (`200 OK`):**
    ```json
    {
      "student_id": "82f41586-7a24-49de-8fab-9f2e0df0dfa9",
      "email": "student@gmail.com",
      "full_name": "Nguyễn Văn A",
      "is_active": true
    }
    ```

### 2.4 Đăng xuất (`POST /logout`)
Gợi ý phía Client xóa Token khỏi Local Storage.

*   **URL:** `/logout`
*   **Method:** `POST`
*   **Authentication Required:** `Bearer <JWT_TOKEN>` trong Header.
*   **Response Thành công (`200 OK`):**
    ```json
    {
      "message": "Đăng xuất thành công. Vui lòng xóa token ở client."
    }
    ```

---

## 🧠 3. API DỊCH VỤ TRẮC NGHIỆM RIASEC (`riasec_service`)
> **Base URL:** `http://localhost:8000/api/riasec` (Thông qua API Gateway)  
> **Định dạng dữ liệu:** `application/json`

### 3.1 Gửi Câu trả lời / Nhận Câu hỏi tiếp theo (`POST /chat`)
API Hợp nhất (1-API Flow): Quản lý toàn bộ vòng lặp trò chuyện. Trả về câu hỏi tiếp theo dựa trên phân tích câu trả lời trước đó, đồng thời tự động đồng bộ hóa điểm tích lũy của học sinh sang bảng `users` ở background.

*   **URL:** `/chat`
*   **Method:** `POST`
*   **Authentication Optional/Required:** `Bearer <JWT_TOKEN>` trong Header.  
    *(Lưu ý: Nếu bật `AUTH_ENABLED=true`, Backend tự lấy student_id từ JWT Token và bỏ qua Body. Nếu tắt bảo mật, Backend  bắn ngay lỗi HTTP 400 Bad Request kèm thông báo lỗi trực quan: {"detail": "student_id is required"}).*
*   **Body (JSON):**
    ```json
    {
      "answer": "Em rất thích vẽ, thỉnh thoảng có thiết kế ảnh trên máy tính nữa anh ạ" // Gửi null ở tin nhắn đầu tiên để bắt đầu trò chuyện
    }
    ```
*   **Response Trạng thái Đang Tiến Hành (`status: in_progress`):**
    ```json
    {
      "status": "in_progress",
      "session_id": "cd48be96-64cc-406e-ba2e-b08eee564f8d",
      "question_no": 2,
      "message": "Tuyệt vời! Sở thích vẽ và thiết kế thể hiện em là người giàu tính nghệ thuật đấy. Nếu ở lớp em tổ chức làm báo tường, em có muốn phụ trách mảng trang trí và vẽ tranh minh họa không?",
      "confidence": 0.50,
      "scores": {
        "R": 0,
        "I": 0,
        "A": 30,
        "S": 0,
        "E": 0,
        "C": 0
      }
    }
    ```
*   **Response Trạng thái Hoàn Thành (`status: completed`):**  
    *Tự động kích hoạt khi đạt đủ 6-8 câu hỏi và điểm số cách biệt rõ nét, hoặc đạt trần cứng 10 câu.*
    ```json
    {
      "status": "completed",
      "session_id": "cd48be96-64cc-406e-ba2e-b08eee564f8d",
      "question_no": 7,
      "message": "Cảm ơn em đã chia sẻ rất nhiệt tình! Cuộc trò chuyện của chúng ta đã hoàn tất. Em hãy xem kết quả phân tích xu hướng tính cách và ngành nghề gợi ý chi tiết của mình nhé!",
      "confidence": 0.85,
      "scores": {
        "R": 10,
        "I": 75,
        "A": 90,
        "S": 40,
        "E": 20,
        "C": 15
      }
    }
    ```

### 3.2 Lấy kết quả Phân tích & Gợi ý cuối cùng (`GET /sessions/{session_id}/result`)
Truy xuất kết quả phân tích sâu chi tiết nhất sau khi hoàn thành phiên trắc nghiệm.

*   **URL:** `/sessions/{session_id}/result`
*   **Method:** `GET`
*   **Authentication Required:** `Bearer <JWT_TOKEN>` trong Header.
*   **Response Thành công (`200 OK`):**
    ```json
    {
      "session_id": "cd48be96-64cc-406e-ba2e-b08eee564f8d",
      "status": "completed",
      "scores": {
        "R": 10.0,
        "I": 75.0,
        "A": 90.0,
        "S": 40.0,
        "E": 20.0,
        "C": 15.0
      },
      "riasec_code": "AIS",
      "top_groups": ["A", "I"],
      "confidence": 0.85,
      "reasoning": "Kết quả phân tích hội thoại bộc lộ rõ bạn là một cá nhân sở hữu thiên hướng Nghệ thuật (A) vượt trội kết hợp mạnh mẽ với tư duy logic Nghiên cứu (I). Bạn hứng thú cao độ với các công việc sáng tạo tự do, giàu trí tưởng tượng mỹ thuật...",
      "suggested_majors": [
        {
          "group": "Nhóm ngành Công nghệ thông tin",
          "majors": ["Trí tuệ nhân tạo", "Công nghệ web"],
          "fit_reason": "Có tư duy phân tích của nhóm I và sáng tạo thẩm mỹ của nhóm A cực kỳ phù hợp thiết kế và lập trình ứng dụng."
        }
      ]
    }
    ```

---

## 🔄 4. HƯỚNG DẪN CHUYỂN ĐỔI ENGINE TRÍ TUỆ NHÂN TẠO
Hệ thống hỗ trợ chạy song song 2 AI Engine cực đỉnh: **Google Gemini (Mặc định)** và **Groq Llama 3 (Kiểm thử siêu tốc)**. Việc chuyển đổi chỉ mất đúng 5 giây nhờ cấu trúc Router tách biệt hoàn hảo:

### 4.1 Chuyển sang dùng Google Gemini (Mặc định)
Để hệ thống sử dụng sức mạnh lập luận đa phương tiện sâu sắc của **Google Gemini**, hãy sửa file `riasec_service/app/main.py`:

```python
# 1. Import router của Gemini
from app.api.endpoints import riasec

# 2. Cài đặt tiêu đề OpenAPI
app = FastAPI(title="RIASEC Service (Gemini Pro)")

# 3. Nạp Router của Gemini vào Endpoint chính
app.include_router(riasec.router, prefix="/api/riasec", tags=["RIASEC"])
```

### 4.2 Chuyển sang dùng Groq Llama 3 (Kiểm thử siêu tốc)
Để hệ thống sử dụng tốc độ phản hồi cực nhanh dưới 1 giây của **Groq Llama 3.3 70B**, hãy sửa file `riasec_service/app/main.py`:

```python
# 1. Import router của Groq
from app.api.endpoints import riasec_groq

# 2. Cài đặt tiêu đề OpenAPI
app = FastAPI(title="RIASEC Service (Groq Super Speed)")

# 3. Nạp Router của Groq vào Endpoint chính
app.include_router(riasec_groq.router, prefix="/api/riasec", tags=["RIASEC"])
```

Sau khi sửa đổi, bạn chỉ cần chạy lệnh build lại Docker Container để áp dụng ngay lập tức:
```bash
docker compose down && docker compose up -d --build
```
