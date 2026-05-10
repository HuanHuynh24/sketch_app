# Profile Service — API Documentation

**Base URL (Docker):** `http://localhost:8001`  
**Base URL (qua API Gateway):** `http://localhost:8000`  
**Swagger UI:** `http://localhost:8001/docs`  
**Version:** 1.0.0

---

## Tổng quan

Profile Service quản lý xác thực người dùng (đăng ký, đăng nhập) và thông tin hồ sơ cá nhân. Tất cả endpoint bảo mật sử dụng **JWT Bearer Token** theo chuẩn OAuth2.

### Authentication

Các endpoint có ký hiệu 🔒 yêu cầu header:

```
Authorization: Bearer <access_token>
```

Token lấy từ response của `/api/profile/login`.

---

## Endpoints

### Health Check

---

#### `GET /health`

Kiểm tra trạng thái service.

**Auth:** Không cần

**Response `200 OK`**
```json
{
  "status": "ok",
  "service": "profile_service"
}
```

---

### Authentication & Profile

Base path: `/api/profile`

---

#### `POST /api/profile/register`

Đăng ký tài khoản mới.

**Auth:** Không cần

**Request Body** `application/json`

| Field | Type | Bắt buộc | Mô tả |
|---|---|---|---|
| `email` | string | ✅ | Địa chỉ email (phải unique) |
| `password` | string | ✅ | Mật khẩu, 6–50 ký tự |
| `full_name` | string | ✅ | Họ và tên đầy đủ |

```json
{
  "email": "nguyen.van.a@example.com",
  "password": "matkhau123",
  "full_name": "Nguyễn Văn A"
}
```

**Response `201 Created`**

```json
{
  "id": 1,
  "email": "nguyen.van.a@example.com",
  "full_name": "Nguyễn Văn A",
  "is_active": true
}
```

**Error Responses**

| Status | Mô tả |
|---|---|
| `400 Bad Request` | Email đã tồn tại trong hệ thống |
| `422 Unprocessable Entity` | Dữ liệu không hợp lệ (thiếu field, password quá ngắn...) |

```json
{
  "detail": "Email này đã được sử dụng."
}
```

---

#### `POST /api/profile/login`

Đăng nhập và lấy JWT Access Token.

**Auth:** Không cần

**Request Body** `application/x-www-form-urlencoded`

> ⚠️ Endpoint này dùng **form data** (không phải JSON) theo chuẩn OAuth2 Password Flow.  
> Trên Swagger UI có thể dùng nút **Authorize** để đăng nhập trực tiếp.

| Field | Type | Bắt buộc | Mô tả |
|---|---|---|---|
| `username` | string | ✅ | Địa chỉ email của người dùng |
| `password` | string | ✅ | Mật khẩu |

**Ví dụ với curl:**
```bash
curl -X POST http://localhost:8001/api/profile/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=nguyen.van.a@example.com&password=matkhau123"
```

**Ví dụ với Postman:**
- Method: `POST`
- Body: `x-www-form-urlencoded`
- Key `username` → value: email
- Key `password` → value: mật khẩu

**Response `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**

| Status | Mô tả |
|---|---|
| `401 Unauthorized` | Sai email hoặc mật khẩu |
| `422 Unprocessable Entity` | Thiếu field bắt buộc |

```json
{
  "detail": "Sai email hoặc mật khẩu"
}
```

---

#### `GET /api/profile/me` 🔒

Lấy thông tin cá nhân của người dùng đang đăng nhập.

**Auth:** Bearer Token bắt buộc

**Headers**
```
Authorization: Bearer <access_token>
```

**Response `200 OK`**

```json
{
  "id": 1,
  "email": "nguyen.van.a@example.com",
  "full_name": "Nguyễn Văn A",
  "is_active": true
}
```

**Error Responses**

| Status | Mô tả |
|---|---|
| `401 Unauthorized` | Token không hợp lệ, hết hạn, hoặc không có token |
| `403 Forbidden` | Token hợp lệ nhưng không có quyền |

```json
{
  "detail": "Không thể xác thực thông tin (Token không hợp lệ)."
}
```

---

## Data Models

### UserCreate (Request)

```json
{
  "email": "string",
  "password": "string (6-50 ký tự)",
  "full_name": "string"
}
```

### UserResponse (Response)

```json
{
  "id": "integer",
  "email": "string",
  "full_name": "string",
  "is_active": "boolean"
}
```

### Token (Response)

```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer"
}
```

---

## Database Schema

**Bảng:** `users`

| Column | Type | Constraint | Mô tả |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | ID người dùng |
| `email` | VARCHAR | UNIQUE, NOT NULL, INDEX | Địa chỉ email |
| `full_name` | VARCHAR | NOT NULL | Họ và tên |
| `hashed_password` | VARCHAR | NOT NULL | Mật khẩu đã hash (bcrypt) |
| `is_active` | BOOLEAN | DEFAULT true | Trạng thái tài khoản |

---

## JWT Token

- **Algorithm:** HS256
- **Expiry:** 60 phút (mặc định)
- **Payload:**
  ```json
  {
    "sub": "nguyen.van.a@example.com",
    "exp": 1234567890
  }
  ```

> Token được verify bởi **API Gateway** trước khi forward request đến các service khác.  
> Các service nội bộ nhận `X-User-Id` header (email) từ Gateway thay vì verify token trực tiếp.

---

## Ví dụ luồng đầy đủ

### 1. Đăng ký

```bash
curl -X POST http://localhost:8001/api/profile/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Đăng nhập lấy token

```bash
curl -X POST http://localhost:8001/api/profile/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

### 3. Lấy thông tin cá nhân

```bash
curl -X GET http://localhost:8001/api/profile/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Postman Quick Setup

1. Tạo collection **Profile Service**
2. Tạo collection variable `base_url` = `http://localhost:8001`
3. Sau khi login, lưu token vào variable `token`
4. Các request bảo mật dùng: `Authorization: Bearer {{token}}`

**Test script tự động lưu token** (tab Tests của request Login):
```javascript
const json = pm.response.json();
if (json.access_token) {
    pm.collectionVariables.set("token", json.access_token);
    console.log("✅ Token saved");
}
```
