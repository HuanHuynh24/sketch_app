# FE API Guide

Tài liệu này hướng dẫn Frontend gọi Backend qua API Gateway trong môi trường local.

FE chỉ gọi gateway:

```txt
http://localhost:8000
```

Không gọi trực tiếp các service nội bộ:

```txt
http://localhost:8001  profile_service
http://localhost:8002  riasec_service
http://localhost:8003  admission_service
http://localhost:8004  rag_service
```

## 1. Cấu Hình FE

Với Next.js, tạo `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

```ts
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
```

## 2. Quy Tắc Gọi API

Prefix chính:

```txt
Profile: /api/profile
RIASEC : /api/riasec
```

API cần đăng nhập phải gửi:

```txt
Authorization: Bearer ACCESS_TOKEN
```

Sau đăng ký/đăng nhập, FE lưu token:

```ts
localStorage.setItem("access_token", data.access_token);
localStorage.setItem("student", JSON.stringify(data.student));
```

Không gửi `student_id` khi gọi RIASEC. Backend tự lấy học sinh hiện tại từ token qua Profile Service.

## 3. API Client Gợi Ý

```ts
type ApiOptions = RequestInit & {
  auth?: boolean;
};

export async function apiFetch<T>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const headers = new Headers(options.headers);

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

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
      message = typeof error.detail === "string"
        ? error.detail
        : JSON.stringify(error.detail);
    } catch {
      message = await res.text();
    }

    throw new Error(message);
  }

  return res.json();
}
```

## 4. Auth APIs

### Đăng Ký

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
    "dob": "2007-05-20",
    "province": "Khanh Hoa",
    "area_code": "KV2",
    "priority_group": "01",
    "target_province": "TP.HCM",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-05-17T10:00:00",
    "updated_at": "2026-05-17T10:00:00"
  }
}
```

### Đăng Nhập

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

Response giống API đăng ký.

### Lấy Học Sinh Hiện Tại

```txt
GET /api/profile/auth/me
Authorization: Bearer ACCESS_TOKEN
```

FE nên gọi API này khi reload app để kiểm tra token còn hợp lệ.

## 5. RIASEC Flow Mới Nhất

Flow chính:

```txt
1. POST /api/riasec/sessions
2. Render response.assistant_messages theo thứ tự
3. User trả lời câu hỏi cuối trong assistant_messages
4. POST /api/riasec/sessions/{session_id}/answers
5. Render response.user_message và response.assistant_messages
6. Nếu status = completed: dừng input, lấy dcp_id, mở màn kết quả
7. GET /api/riasec/profiles/{dcp_id}
```

Lưu ý quan trọng:

- `assistant_message` vẫn còn để tương thích, luôn là message chính cuối cùng backend muốn FE chú ý.
- `assistant_messages` là mảng message mới, FE nên ưu tiên render mảng này để có intro/transition/lead-in tự nhiên.
- `current_step` là số câu trả lời hợp lệ đã được chấm.
- Nếu câu trả lời không hợp lệ, `current_step` không tăng.
- Khi `session.status === "completed"`, FE phải disable input. Nếu vẫn gọi `POST /answers`, backend trả `400` với `detail = "Session is not in progress"`.

## 6. Tạo Phiên RIASEC

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
    "entropy": 0,
    "current_focus_groups": [],
    "riasec_code": null,
    "termination_reason": null,
    "final_summary": null,
    "created_at": "2026-05-17T10:00:00",
    "updated_at": "2026-05-17T10:00:00",
    "completed_at": null
  },
  "question": {
    "message_id": "uuid",
    "session_id": "uuid",
    "role": "assistant",
    "content": "Gian hàng hướng nghiệp của lớp sắp mở cửa...",
    "message_type": "anchor_scenario",
    "metadata_json": {
      "type": "anchor_scenario",
      "content": "Gian hàng hướng nghiệp của lớp sắp mở cửa...",
      "focus_groups": ["R", "I", "A", "S", "E", "C"],
      "context": "anchor",
      "question_style": "role_choice"
    },
    "riasec_signal": null,
    "created_at": "2026-05-17T10:00:00"
  },
  "assistant_messages": [
    {
      "message_type": "intro",
      "content": "Chào bạn, mình sẽ hỏi vài tình huống ngắn..."
    },
    {
      "message_type": "intro",
      "content": "Không có đáp án đúng sai đâu..."
    },
    {
      "message_type": "question_lead_in",
      "content": "Mình bắt đầu bằng một tình huống đầu tiên nhé:"
    },
    {
      "message_type": "anchor_scenario",
      "content": "Gian hàng hướng nghiệp của lớp sắp mở cửa..."
    }
  ]
}
```

FE:

```ts
export async function startRiasecSession() {
  return apiFetch<StartRiasecResponse>("/api/riasec/sessions", {
    method: "POST",
    auth: true,
  });
}
```

Render:

```ts
setSession(data.session);
setMessages(data.assistant_messages.length > 0
  ? data.assistant_messages
  : [data.question]
);
```

## 7. Gửi Câu Trả Lời

```txt
POST /api/riasec/sessions/{session_id}/answers
Authorization: Bearer ACCESS_TOKEN
```

Request:

```json
{
  "answer_text": "Em sẽ phân tích thông tin trước vì em muốn biết học sinh đang quan tâm ngành nào, sau đó mới đề xuất cách trình bày cho gian hàng."
}
```

`answer_text` bắt buộc từ 1 đến 3000 ký tự.

### 7.1. Response Tiếp Tục

```json
{
  "status": "in_progress",
  "session": {
    "session_id": "uuid",
    "status": "in_progress",
    "current_step": 1,
    "scores": {
      "R": 0,
      "I": 1.5,
      "A": 0.5,
      "S": 0,
      "E": 0,
      "C": 0.5
    },
    "confidence": {
      "R": 0,
      "I": 0.75,
      "A": 0.25,
      "S": 0,
      "E": 0,
      "C": 0.25
    },
    "current_focus_groups": ["A", "C"],
    "riasec_code": "IAC"
  },
  "user_message": {
    "message_type": "answer",
    "content": "Em sẽ phân tích thông tin trước...",
    "riasec_signal": {
      "scores": {
        "R": 0,
        "I": 1.5,
        "A": 0.5,
        "S": 0,
        "E": 0,
        "C": 0.5
      },
      "confidence": {
        "R": 0,
        "I": 0.75,
        "A": 0.25,
        "S": 0,
        "E": 0,
        "C": 0.25
      },
      "focus_groups": ["R", "I", "A", "S", "E", "C"],
      "primary_groups": ["I"],
      "detected_traits": ["phân tích thông tin"],
      "evidence": [
        {
          "group": "I",
          "quote": "phân tích thông tin",
          "strength": 1.5,
          "confidence": 0.75
        }
      ],
      "reasoning": "Câu trả lời thể hiện xu hướng phân tích dữ liệu trước khi đề xuất giải pháp.",
      "scenario_message_id": "uuid",
      "scenario_type": "anchor_scenario"
    }
  },
  "assistant_message": {
    "message_type": "adaptive_scenario",
    "content": "Video giới thiệu ngành của lớp đang bị nhận xét là vừa thiếu thông tin vừa chưa cuốn..."
  },
  "assistant_messages": [
    {
      "message_type": "transition",
      "content": "Mình ghi nhận cách bạn xử lý tình huống này..."
    },
    {
      "message_type": "adaptive_scenario",
      "content": "Video giới thiệu ngành của lớp đang bị nhận xét là vừa thiếu thông tin vừa chưa cuốn..."
    }
  ],
  "dcp_id": null
}
```

FE:

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

Render response tiếp tục:

```ts
setSession(data.session);
setWarning(null);
setAnswerText("");
setMessages((prev) => [
  ...prev,
  data.user_message,
  ...(data.assistant_messages.length > 0
    ? data.assistant_messages
    : data.assistant_message
      ? [data.assistant_message]
      : []),
]);
```

### 7.2. Response Câu Trả Lời Không Hợp Lệ

```json
{
  "status": "in_progress",
  "session": {
    "status": "in_progress",
    "current_step": 1
  },
  "user_message": {
    "message_type": "invalid_answer",
    "content": "abc",
    "metadata_json": {
      "quality_check": {
        "is_valid": false,
        "reason": "too_short",
        "warning_message": "Câu trả lời của bạn chưa đủ rõ..."
      }
    }
  },
  "assistant_message": {
    "message_type": "answer_warning",
    "content": "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm..."
  },
  "assistant_messages": [
    {
      "message_type": "answer_reflection",
      "content": "Mình chưa đủ thông tin để hiểu lựa chọn của bạn trong tình huống này."
    },
    {
      "message_type": "answer_warning",
      "content": "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm..."
    }
  ],
  "dcp_id": null
}
```

FE xử lý:

```ts
if (data.assistant_message?.message_type === "answer_warning") {
  setWarning(data.assistant_message.content);
  setMessages((prev) => [
    ...prev,
    data.user_message,
    ...(data.assistant_messages.length > 0
      ? data.assistant_messages
      : [data.assistant_message]),
  ]);
  return;
}
```

Không tăng progress, không đổi câu hỏi chính.

### 7.3. Response Hoàn Tất

```json
{
  "status": "completed",
  "session": {
    "session_id": "uuid",
    "status": "completed",
    "current_step": 5,
    "riasec_code": "IAC",
    "termination_reason": "Confidence threshold reached",
    "final_summary": "Kết quả hiện tại cho thấy..."
  },
  "assistant_message": {
    "message_type": "final_result",
    "content": "Bài đánh giá đã hoàn tất. Mã RIASEC của bạn là IAC...",
    "metadata_json": {
      "dcp_id": "uuid",
      "riasec_code": "IAC",
      "termination_reason": "Confidence threshold reached",
      "radar_chart": {},
      "dominant_groups": [],
      "group_analysis": [],
      "career_recommendations": {}
    }
  },
  "assistant_messages": [
    {
      "message_type": "completion_lead_in",
      "content": "Cảm ơn bạn. Mình đã có đủ dữ liệu để tổng hợp xu hướng RIASEC của bạn..."
    },
    {
      "message_type": "final_result",
      "content": "Bài đánh giá đã hoàn tất. Mã RIASEC của bạn là IAC..."
    }
  ],
  "dcp_id": "uuid"
}
```

FE xử lý:

```ts
if (data.status === "completed" && data.dcp_id) {
  setSession(data.session);
  setIsCompleted(true);
  setInputDisabled(true);
  router.push(`/riasec/result/${data.dcp_id}`);
  return;
}
```

Màn kết quả nên gọi lại `GET /api/riasec/profiles/{dcp_id}` để lấy dữ liệu chuẩn.

## 8. Lấy Kết Quả RIASEC

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
    "R": 1,
    "I": 6,
    "A": 4,
    "S": 2,
    "E": 1,
    "C": 3
  },
  "confidence": {
    "R": 0.2,
    "I": 0.85,
    "A": 0.7,
    "S": 0.4,
    "E": 0.2,
    "C": 0.6
  },
  "career_groups": [
    "Công nghệ thông tin",
    "Khoa học cơ bản",
    "Khoa học dữ liệu",
    "Báo chí",
    "Truyền thông",
    "Kinh doanh"
  ],
  "digital_competencies": {
    "I": ["Phân tích dữ liệu", "Tư duy logic"],
    "A": ["Sáng tạo nội dung số", "Thiết kế trải nghiệm"],
    "C": ["Quản lý dữ liệu", "Tự động hóa quy trình"]
  },
  "recommended_majors": [
    "Khoa học máy tính",
    "Công nghệ phần mềm",
    "Khoa học dữ liệu",
    "Truyền thông đa phương tiện",
    "Thiết kế UX/UI",
    "Kế toán"
  ],
  "summary": "Kết quả hiện tại cho thấy bạn nổi bật ở nhóm IAC...",
  "created_at": "2026-05-17T10:10:00",
  "radar_chart": {
    "type": "riasec_radar",
    "max_score": 14,
    "axes": [
      {
        "group": "R",
        "label": "Thực tế - Kỹ thuật",
        "score": 1,
        "max_score": 14,
        "normalized_score": 7.14,
        "confidence": 0.2,
        "description": "Thích làm việc trực tiếp với máy móc, công cụ, thiên nhiên, vật liệu hoặc các hoạt động có thao tác cụ thể và kết quả nhìn thấy được."
      }
    ]
  },
  "dominant_groups": [
    {
      "group": "I",
      "label": "Nghiên cứu - Phân tích",
      "score": 6,
      "confidence": 0.85,
      "description": "Thích quan sát, đặt câu hỏi, phân tích dữ liệu, tìm nguyên nhân và giải quyết vấn đề bằng logic hoặc phương pháp khoa học."
    }
  ],
  "group_analysis": [
    {
      "group": "I",
      "name": "Investigative",
      "label": "Nghiên cứu - Phân tích",
      "score": 6,
      "confidence": 0.85,
      "level": "medium",
      "description": "Thích quan sát, đặt câu hỏi, phân tích dữ liệu, tìm nguyên nhân và giải quyết vấn đề bằng logic hoặc phương pháp khoa học.",
      "career_groups": ["Công nghệ thông tin", "Khoa học cơ bản", "Khoa học dữ liệu"],
      "recommended_majors": ["Khoa học máy tính", "Công nghệ phần mềm", "Khoa học dữ liệu"],
      "suitable_roles": ["Backend Developer", "Data Analyst", "AI Engineer"],
      "digital_competencies": ["Phân tích dữ liệu", "Tư duy logic"]
    }
  ],
  "career_recommendations": {
    "riasec_code": "IAC",
    "career_groups": ["Công nghệ thông tin", "Khoa học cơ bản", "Khoa học dữ liệu"],
    "recommended_majors": ["Khoa học máy tính", "Công nghệ phần mềm", "Khoa học dữ liệu"],
    "suitable_roles": ["Backend Developer", "Data Analyst", "AI Engineer"],
    "digital_competencies": {
      "I": ["Phân tích dữ liệu", "Tư duy logic"],
      "A": ["Sáng tạo nội dung số", "Thiết kế trải nghiệm"],
      "C": ["Quản lý dữ liệu", "Tự động hóa quy trình"]
    }
  }
}
```

## 9. Render Radar Chart Và Kết Quả

Dùng:

```ts
const axes = profile.radar_chart?.axes ?? [];
```

Map cho chart:

```ts
const radarData = axes.map((axis) => ({
  group: axis.group,
  label: axis.label,
  score: axis.normalized_score,
  rawScore: axis.score,
  maxScore: axis.max_score,
  confidence: axis.confidence,
  description: axis.description,
}));
```

Gợi ý render:

```txt
Radar chart        : radar_chart.axes[].normalized_score
Top nhóm nổi bật   : dominant_groups
Phân tích từng nhóm: group_analysis
Ngành/nghề phù hợp : career_recommendations
Summary            : summary hoặc session.final_summary
```

## 10. TypeScript Types

```ts
export type RiasecGroup = "R" | "I" | "A" | "S" | "E" | "C";
export type RiasecScore = Record<RiasecGroup, number>;
export type RiasecStatus = "in_progress" | "completed";

export type RiasecMessageType =
  | "intro"
  | "question_lead_in"
  | "anchor_scenario"
  | "adaptive_scenario"
  | "transition"
  | "answer"
  | "invalid_answer"
  | "answer_reflection"
  | "answer_warning"
  | "completion_lead_in"
  | "final_result";

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

export interface RiasecEvidence {
  group: RiasecGroup;
  quote: string | null;
  strength: number;
  confidence: number;
}

export interface RiasecSignal {
  scores?: Partial<RiasecScore>;
  confidence?: Partial<RiasecScore>;
  focus_groups?: RiasecGroup[];
  primary_groups?: RiasecGroup[];
  detected_traits?: string[];
  evidence?: RiasecEvidence[];
  reasoning?: string;
  scenario_message_id?: string | null;
  scenario_type?: string | null;
}

export interface RiasecMessage {
  message_id: string;
  session_id: string;
  role: "assistant" | "user" | "system";
  content: string;
  message_type: RiasecMessageType;
  metadata_json?: Record<string, unknown> | null;
  riasec_signal?: RiasecSignal | null;
  created_at: string;
}

export interface StartRiasecResponse {
  session: RiasecSession;
  question: RiasecMessage;
  assistant_messages: RiasecMessage[];
}

export interface SubmitAnswerResponse {
  status: RiasecStatus;
  session: RiasecSession;
  user_message: RiasecMessage;
  assistant_message: RiasecMessage | null;
  assistant_messages: RiasecMessage[];
  dcp_id: string | null;
}

export interface RadarAxis {
  group: RiasecGroup;
  label: string;
  score: number;
  max_score: number;
  normalized_score: number;
  confidence: number;
  description: string;
}

export interface RadarChart {
  type: "riasec_radar";
  max_score: number;
  axes: RadarAxis[];
}

export interface DominantGroup {
  group: RiasecGroup;
  label: string;
  score: number;
  confidence: number;
  description: string;
}

export interface GroupAnalysis {
  group: RiasecGroup;
  name: string;
  label: string;
  score: number;
  confidence: number;
  level: "low" | "emerging" | "medium" | "high";
  description: string;
  career_groups: string[];
  recommended_majors: string[];
  suitable_roles: string[];
  digital_competencies: string[];
}

export interface CareerRecommendations {
  riasec_code: string;
  career_groups: string[];
  recommended_majors: string[];
  suitable_roles: string[];
  digital_competencies: Partial<Record<RiasecGroup, string[]>>;
}

export interface DigitalCompetencyProfile {
  dcp_id: string;
  student_id: string;
  session_id: string;
  riasec_code: string;
  scores: RiasecScore;
  confidence: RiasecScore;
  career_groups: string[];
  digital_competencies: Partial<Record<RiasecGroup, string[]>>;
  recommended_majors: string[];
  summary: string;
  created_at: string;
  radar_chart: RadarChart | null;
  dominant_groups: DominantGroup[] | null;
  group_analysis: GroupAnalysis[] | null;
  career_recommendations: CareerRecommendations | null;
}
```

## 11. UI Checklist

Khi bắt đầu:

1. Kiểm tra token.
2. Gọi `POST /api/riasec/sessions`.
3. Render `assistant_messages`.
4. Lưu `session_id`.

Khi gửi answer:

1. Disable nút gửi trong lúc loading.
2. Gọi `POST /api/riasec/sessions/{session_id}/answers`.
3. Render `user_message`.
4. Render `assistant_messages`.
5. Nếu `assistant_message.message_type === "answer_warning"`:
   - Hiển thị warning.
   - Không tăng progress thủ công.
   - Giữ input cho user trả lời lại cùng câu hỏi.
6. Nếu `status === "in_progress"`:
   - Clear warning.
   - Clear textarea.
   - Cập nhật `session`, `scores`, `confidence`.
7. Nếu `status === "completed"`:
   - Disable input.
   - Lưu `dcp_id`.
   - Điều hướng sang màn kết quả.
   - Gọi `GET /api/riasec/profiles/{dcp_id}`.

Progress:

```ts
const answered = session.current_step;
const total = session.max_steps;
const percent = Math.round((answered / total) * 100);
const displayQuestionNo = Math.min(session.current_step + 1, session.max_steps);
```

Disable input:

```ts
const inputDisabled = loading || session?.status === "completed";
```

## 12. Error Handling

Các lỗi thường gặp:

```txt
400: Request không hợp lệ hoặc session không còn in_progress
401: Token sai hoặc hết hạn
403: Không có quyền truy cập session/profile
404: Không tìm thấy resource
422: Body không đúng schema, ví dụ answer_text rỗng
502: Gateway hoặc service proxy lỗi
504: Service timeout
```

Trường hợp hay gặp nhất sau khi hoàn tất bài test:

```json
{
  "detail": "Session is not in progress"
}
```

Nguyên nhân: FE vẫn gọi `POST /answers` sau khi session đã `completed`.

Xử lý:

```ts
if (session?.status === "completed") {
  return;
}
```

Xử lý `401`:

```ts
localStorage.removeItem("access_token");
localStorage.removeItem("student");
router.push("/login");
```

## 13. API FE Cần Dùng

Flow chính chỉ cần:

```txt
POST /api/profile/auth/register
POST /api/profile/auth/login
GET  /api/profile/auth/me
POST /api/riasec/sessions
POST /api/riasec/sessions/{session_id}/answers
GET  /api/riasec/profiles/{dcp_id}
```
