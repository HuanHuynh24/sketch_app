# FE API Guide

Tài liệu này mô tả cách Frontend gọi Backend qua API Gateway.

Frontend không gọi trực tiếp `profile_service`, `riasec_service`, `admission_service` hoặc `rag_service`. Trong môi trường dev, FE chỉ cần gọi một base URL:

```txt
http://localhost:8000
```

## 1. Cấu hình môi trường FE

Với Next.js, tạo file `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Trong code FE:

```ts
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
```

## 2. Quy tắc gọi API

Tất cả endpoint bên dưới đều đi qua API Gateway:

```txt
Profile: /api/profile/...
RIASEC : /api/riasec/...
```

Các API cần đăng nhập phải gửi header:

```txt
Authorization: Bearer ACCESS_TOKEN
```

FE nên lưu:

```ts
localStorage.setItem("access_token", data.access_token);
localStorage.setItem("student", JSON.stringify(data.student));
```

Không cần lưu `student_id` để gửi cho RIASEC nữa. RIASEC sẽ tự lấy học sinh hiện tại từ token thông qua Profile Service.

## 3. API client gợi ý

```ts
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ApiOptions = RequestInit & {
  auth?: boolean;
};

export async function apiFetch<T>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (options.auth) {
    const token = localStorage.getItem("access_token");

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let message = "Request failed";

    try {
      const error = await res.json();
      message = error.detail ?? message;
    } catch {
      message = await res.text();
    }

    throw new Error(message);
  }

  return res.json();
}
```

## 4. Auth APIs

### Đăng ký học sinh

```txt
POST /api/profile/auth/register
```

Request:

```json
{
  "full_name": "Nguyen Van Test",
  "email": "test_riasec@example.com",
  "password": "123456",
  "province": "Khanh Hoa",
  "area_code": "KV2",
  "dob": "2007-05-20",
  "priority_group": "01",
  "target_province": "TP.HCM"
}
```

Response:

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600,
  "student": {
    "student_id": "uuid",
    "full_name": "Nguyen Van Test",
    "email": "test_riasec@example.com",
    "province": "Khanh Hoa",
    "area_code": "KV2"
  }
}
```

FE xử lý:

```ts
export async function registerStudent(payload: RegisterPayload) {
  const data = await apiFetch<AuthResponse>("/api/profile/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("student", JSON.stringify(data.student));

  return data;
}
```

### Đăng nhập

```txt
POST /api/profile/auth/login
```

Request:

```json
{
  "email": "test_riasec@example.com",
  "password": "123456"
}
```

FE xử lý giống đăng ký: lưu `access_token` và `student`.

### Lấy thông tin học sinh hiện tại

```txt
GET /api/profile/auth/me
Authorization: Bearer ACCESS_TOKEN
```

FE dùng API này để kiểm tra trạng thái đăng nhập khi reload trang.

Nếu API trả `401`, FE nên xóa token và chuyển về màn đăng nhập.

```ts
export async function getMe() {
  return apiFetch<Student>("/api/profile/auth/me", {
    method: "GET",
    auth: true,
  });
}
```

## 5. RIASEC APIs

Các API RIASEC đều đi qua Gateway và dùng token từ Profile Service.

### Tạo phiên RIASEC

```txt
POST /api/riasec/sessions
Authorization: Bearer ACCESS_TOKEN
```

Không gửi body.

Response:

```json
{
  "session": {
    "session_id": "uuid",
    "student_id": "uuid",
    "status": "in_progress",
    "current_step": 0,
    "min_steps": 5,
    "max_steps": 7,
    "scores": {
      "R": 0,
      "I": 0,
      "A": 0,
      "S": 0,
      "E": 0,
      "C": 0
    },
    "confidence": {
      "R": 0,
      "I": 0,
      "A": 0,
      "S": 0,
      "E": 0,
      "C": 0
    },
    "riasec_code": null
  },
  "question": {
    "message_id": "uuid",
    "session_id": "uuid",
    "role": "assistant",
    "message_type": "anchor_scenario",
    "content": "Câu hỏi tình huống đầu tiên...",
    "metadata_json": {
      "type": "anchor_scenario",
      "focus_groups": ["R", "I", "A", "S", "E", "C"],
      "context": "anchor",
      "question_style": "role_choice"
    },
    "created_at": "2026-05-15T..."
  }
}
```

FE xử lý:

```ts
export async function startRiasecSession() {
  return apiFetch<StartRiasecResponse>("/api/riasec/sessions", {
    method: "POST",
    auth: true,
  });
}
```

Lưu trong state:

```ts
setSessionId(data.session.session_id);
setCurrentQuestion(data.question.content);
setCurrentStep(data.session.current_step);
```

### Gửi câu trả lời

```txt
POST /api/riasec/sessions/{session_id}/answers
Authorization: Bearer ACCESS_TOKEN
```

Request:

```json
{
  "answer_text": "Em thích phân tích dữ liệu, tìm xu hướng và đề xuất giải pháp phù hợp."
}
```

Response khi tiếp tục:

```json
{
  "status": "in_progress",
  "session": {
    "session_id": "uuid",
    "status": "in_progress",
    "current_step": 2,
    "riasec_code": "IAC"
  },
  "user_message": {
    "message_type": "answer",
    "content": "..."
  },
  "assistant_message": {
    "message_type": "adaptive_scenario",
    "content": "Câu hỏi tiếp theo..."
  },
  "dcp_id": null
}
```

Response khi câu trả lời không hợp lệ:

```json
{
  "status": "in_progress",
  "session": {
    "current_step": 1
  },
  "user_message": {
    "message_type": "invalid_answer",
    "content": "abc"
  },
  "assistant_message": {
    "message_type": "answer_warning",
    "content": "Câu trả lời của bạn quá ngắn..."
  },
  "dcp_id": null
}
```

FE xử lý warning:

```ts
if (data.assistant_message?.message_type === "answer_warning") {
  setWarning(data.assistant_message.content);
  return;
}
```

Response khi hoàn tất:

```json
{
  "status": "completed",
  "session": {
    "session_id": "uuid",
    "status": "completed",
    "current_step": 7,
    "riasec_code": "IAC",
    "termination_reason": "Reached maximum number of questions"
  },
  "assistant_message": {
    "message_type": "final_result",
    "content": "Bài đánh giá đã hoàn tất..."
  },
  "dcp_id": "uuid"
}
```

FE xử lý:

```ts
export async function submitRiasecAnswer(
  sessionId: string,
  answerText: string
) {
  return apiFetch<SubmitAnswerResponse>(
    `/api/riasec/sessions/${sessionId}/answers`,
    {
      method: "POST",
      auth: true,
      body: JSON.stringify({ answer_text: answerText }),
    }
  );
}
```

Nếu `status === "completed"`, FE lưu `dcp_id` và chuyển sang màn kết quả.

### Lấy kết quả RIASEC

```txt
GET /api/riasec/profiles/{dcp_id}
Authorization: Bearer ACCESS_TOKEN
```

Response:

```json
{
  "dcp_id": "uuid",
  "student_id": "uuid",
  "session_id": "uuid",
  "riasec_code": "IAC",
  "scores": {
    "R": 1.5,
    "I": 5.5,
    "A": 4,
    "S": 2,
    "E": 1.5,
    "C": 3
  },
  "confidence": {
    "R": 0.3,
    "I": 0.8,
    "A": 0.7,
    "S": 0.4,
    "E": 0.3,
    "C": 0.6
  },
  "career_groups": ["Công nghệ thông tin", "Khoa học dữ liệu"],
  "digital_competencies": {
    "I": ["Phân tích dữ liệu", "Tư duy logic"]
  },
  "recommended_majors": ["Công nghệ thông tin", "Khoa học dữ liệu"],
  "summary": "Kết quả hiện tại cho thấy..."
}
```

FE xử lý:

```ts
export async function getRiasecProfile(dcpId: string) {
  return apiFetch<DigitalCompetencyProfile>(
    `/api/riasec/profiles/${dcpId}`,
    {
      method: "GET",
      auth: true,
    }
  );
}
```

## 6. TypeScript types gợi ý

```ts
export type RiasecGroup = "R" | "I" | "A" | "S" | "E" | "C";
export type RiasecScore = Record<RiasecGroup, number>;
export type RiasecStatus = "in_progress" | "completed";

export interface Student {
  student_id: string;
  full_name: string;
  email: string;
  dob?: string | null;
  province: string;
  area_code: string;
  priority_group?: string | null;
  target_province?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  student: Student;
}

export interface RiasecSession {
  session_id: string;
  student_id: string;
  status: RiasecStatus;
  current_step: number;
  min_steps: number;
  max_steps: number;
  scores: RiasecScore;
  confidence: RiasecScore;
  entropy: number;
  current_focus_groups: RiasecGroup[];
  riasec_code?: string | null;
  termination_reason?: string | null;
  final_summary?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface RiasecMessage {
  message_id: string;
  session_id: string;
  role: "assistant" | "user" | "system";
  content: string;
  message_type:
    | "anchor_scenario"
    | "adaptive_scenario"
    | "answer"
    | "invalid_answer"
    | "answer_warning"
    | "final_result";
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
}

export interface StartRiasecResponse {
  session: RiasecSession;
  question: RiasecMessage;
}

export interface SubmitAnswerResponse {
  status: "in_progress" | "completed";
  session: RiasecSession;
  user_message: RiasecMessage;
  assistant_message: RiasecMessage | null;
  dcp_id: string | null;
}

export interface DigitalCompetencyProfile {
  dcp_id: string;
  student_id: string;
  session_id: string;
  riasec_code: string;
  scores: RiasecScore;
  confidence: RiasecScore;
  career_groups: string[];
  digital_competencies: Record<string, string[]>;
  recommended_majors: string[];
  summary: string;
  created_at: string;
}
```

## 7. UI behavior bắt buộc

Khi bắt đầu test:

1. Kiểm tra token có tồn tại.
2. Gọi `POST /api/riasec/sessions`.
3. Hiển thị `response.question.content`.

Khi gửi câu trả lời:

1. Gọi `POST /api/riasec/sessions/{session_id}/answers`.
2. Nếu `assistant_message.message_type === "answer_warning"`:
   - Hiển thị cảnh báo.
   - Không tăng progress.
   - Không đổi câu hỏi.
3. Nếu `status === "in_progress"`:
   - Clear warning.
   - Clear textarea.
   - Hiển thị `assistant_message.content`.
   - Cập nhật `current_step`, `scores`, `confidence`.
4. Nếu `status === "completed"`:
   - Lưu `dcp_id`.
   - Chuyển sang màn kết quả.
   - Gọi `GET /api/riasec/profiles/{dcp_id}`.

Progress:

```ts
const displayStep = Math.min(session.current_step + 1, session.max_steps);
```

Lưu ý: `current_step` là số câu trả lời hợp lệ đã được chấm. Khi user trả lời sai/lạc đề, `current_step` không tăng.

## 8. Error handling

FE nên xử lý các lỗi chính:

```txt
400: dữ liệu gửi lên không hợp lệ
401: token sai hoặc hết hạn
403: không có quyền truy cập session/profile
404: không tìm thấy resource
502: Gateway hoặc RIASEC không gọi được Profile Service
504: service timeout
```

Gợi ý xử lý `401`:

```ts
localStorage.removeItem("access_token");
localStorage.removeItem("student");
router.push("/login");
```

## 9. Các API FE không nên dùng

Không gọi trực tiếp:

```txt
http://localhost:8001
http://localhost:8002
http://localhost:8003
http://localhost:8004
```

Không gửi `student_id` khi tạo RIASEC session:

```txt
POST /api/riasec/sessions
```

API này đã lấy học sinh hiện tại từ `Authorization` token.

Không dùng các API RIASEC cũ:

```txt
GET /api/riasec/sessions/{session_id}
PATCH /api/riasec/sessions/{session_id}/abandon
```

Flow FE chính chỉ cần:

```txt
POST /api/profile/auth/register
POST /api/profile/auth/login
GET  /api/profile/auth/me
POST /api/riasec/sessions
POST /api/riasec/sessions/{session_id}/answers
GET  /api/riasec/profiles/{dcp_id}
```
