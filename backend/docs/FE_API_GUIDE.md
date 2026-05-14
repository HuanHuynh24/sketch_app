# FE API Guide

Tài liệu này mô tả các API FE cần dùng để tích hợp luồng đăng ký học sinh và bài đánh giá RIASEC.

## 1. Base URL

Khi gọi trực tiếp từng service local:

```txt
Profile Service: http://localhost:8001/api/profile
RIASEC Service : http://localhost:8002/api/riasec

Nếu FE gọi qua API Gateway, base URL có thể là:

http://localhost:8000

Trong giai đoạn dev hiện tại, FE có thể gọi trực tiếp từng service.

Ví dụ .env phía FE:

VITE_PROFILE_API_URL=http://localhost:8001/api/profile
VITE_RIASEC_API_URL=http://localhost:8002/api/riasec
2. Luồng chức năng tổng quan
1. User đăng ký hoặc đăng nhập.
2. FE lưu access_token và student_id.
3. User bấm "Bắt đầu bài test RIASEC".
4. FE gọi API tạo RIASEC session.
5. FE hiển thị câu hỏi đầu tiên.
6. User nhập câu trả lời.
7. FE gửi câu trả lời lên BE.
8. Nếu BE trả answer_warning:
   - FE hiển thị cảnh báo.
   - Không chuyển câu mới.
   - Cho user trả lời lại.
9. Nếu BE trả adaptive_scenario:
   - FE hiển thị câu hỏi tiếp theo.
10. Nếu BE trả completed:
   - FE lấy dcp_id.
   - FE gọi API lấy kết quả cuối.
   - FE chuyển sang màn kết quả.
3. API đăng ký học sinh
Mục đích

Tạo tài khoản học sinh mới và nhận về token cùng thông tin học sinh.

Endpoint
POST /auth/register

Full URL:

http://localhost:8001/api/profile/auth/register
Request body
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
Giải thích input
Field	Type	Required	Mô tả
full_name	string	Yes	Họ tên học sinh
email	string	Yes	Email đăng nhập
password	string	Yes	Mật khẩu
province	string	No	Tỉnh/thành hiện tại
area_code	string	No	Khu vực ưu tiên
dob	string	No	Ngày sinh, format YYYY-MM-DD
priority_group	string	No	Nhóm ưu tiên
target_province	string	No	Tỉnh/thành mong muốn học
Response thành công
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "student": {
    "student_id": "uuid",
    "full_name": "Nguyen Van Test",
    "email": "test_riasec@example.com"
  }
}
FE cần lưu
localStorage.setItem("access_token", response.access_token);
localStorage.setItem("student_id", response.student.student_id);
Lỗi thường gặp
Email đã tồn tại

BE có thể trả lỗi 400.

FE nên hiển thị:

Email này đã được sử dụng. Vui lòng đăng nhập hoặc dùng email khác.
4. API đăng nhập học sinh
Mục đích

Đăng nhập tài khoản đã có.

Endpoint
POST /auth/login

Full URL:

http://localhost:8001/api/profile/auth/login
Request body

Tùy implementation hiện tại của profile_service. Nếu login dùng JSON:

{
  "email": "test_riasec@example.com",
  "password": "123456"
}

Nếu login dùng OAuth2 form, FE cần gửi dạng form-data hoặc x-www-form-urlencoded.

Response thành công
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "student": {
    "student_id": "uuid",
    "email": "test_riasec@example.com"
  }
}
FE cần lưu
localStorage.setItem("access_token", response.access_token);
localStorage.setItem("student_id", response.student.student_id);
5. API lấy thông tin học sinh hiện tại
Mục đích

Kiểm tra token và lấy thông tin học sinh đang đăng nhập.

Endpoint
GET /auth/me

Full URL:

http://localhost:8001/api/profile/auth/me
Headers
Authorization: Bearer ACCESS_TOKEN
Response thành công
{
  "student_id": "uuid",
  "full_name": "Nguyen Van Test",
  "email": "test_riasec@example.com",
  "province": "Khánh Hòa",
  "area_code": "KV2",
  "dob": "2007-05-20",
  "priority_group": "01",
  "target_province": "TP.HCM"
}
FE xử lý
Nếu thành công: user vẫn đăng nhập.
Nếu lỗi 401: xóa token và chuyển về màn login.
if (error.response?.status === 401) {
  localStorage.removeItem("access_token");
  localStorage.removeItem("student_id");
}
6. API tạo RIASEC session
Mục đích

Khởi tạo một phiên làm bài test RIASEC cho học sinh.

API này sẽ:

Tạo session_id.
Sinh câu hỏi đầu tiên dạng anchor_scenario.
Khởi tạo điểm RIASEC ban đầu.
Endpoint
POST /sessions

Full URL:

http://localhost:8002/api/riasec/sessions
Request body
{
  "student_id": "uuid"
}
Giải thích input
Field	Type	Required	Mô tả
student_id	UUID	Yes	ID học sinh lấy từ Profile Service
Response thành công
{
  "session": {
    "session_id": "uuid",
    "student_id": "uuid",
    "status": "in_progress",
    "current_step": 0,
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
    "content": "Trường bạn tổ chức một dự án...",
    "metadata_json": {
      "type": "anchor_scenario",
      "focus_groups": ["R", "I", "A", "S", "E", "C"],
      "context": "anchor",
      "question_style": "role_choice"
    },
    "created_at": "2026-05-14T..."
  }
}
FE cần lưu
setSessionId(response.session.session_id);
setCurrentQuestion(response.question.content);
setCurrentStep(response.session.current_step);
Lỗi thường gặp
student_id không tồn tại

Có thể trả 404 hoặc 400.

FE nên xử lý:

Không tìm thấy thông tin học sinh. Vui lòng đăng nhập lại.
7. API gửi câu trả lời RIASEC
Mục đích

Gửi câu trả lời của học sinh cho câu hỏi hiện tại.

BE sẽ:

Kiểm tra câu trả lời có nghiêm túc không.
Nếu không hợp lệ: trả cảnh báo, không tăng step.
Nếu hợp lệ:
Chấm điểm RIASEC.
Cập nhật score/confidence.
Sinh câu hỏi tiếp theo.
Hoặc hoàn tất nếu đủ điều kiện.
Endpoint
POST /sessions/{session_id}/answers

Full URL:

http://localhost:8002/api/riasec/sessions/{session_id}/answers
Path params
Param	Type	Required	Mô tả
session_id	UUID	Yes	ID phiên RIASEC
Request body
{
  "answer_text": "Em thích phân tích dữ liệu, tìm ra xu hướng và đề xuất giải pháp phù hợp."
}
Giải thích input
Field	Type	Required	Mô tả
answer_text	string	Yes	Câu trả lời tự nhiên của học sinh
Case 1: Câu trả lời không hợp lệ

Ví dụ gửi:

{
  "answer_text": "abc"
}

Response:

{
  "status": "in_progress",
  "session": {
    "session_id": "uuid",
    "status": "in_progress",
    "current_step": 1
  },
  "user_message": {
    "message_type": "invalid_answer",
    "content": "abc"
  },
  "assistant_message": {
    "message_type": "answer_warning",
    "content": "Câu trả lời của bạn quá ngắn nên hệ thống chưa thể đánh giá. Hãy nói rõ bạn sẽ chọn hướng nào và vì sao.",
    "metadata_json": {
      "reason": "Câu trả lời quá ngắn để đánh giá.",
      "repeat_question": "..."
    }
  },
  "dcp_id": null
}
FE xử lý khi answer_warning

Nếu:

response.assistant_message.message_type === "answer_warning"

Thì FE cần:

Hiển thị warning.
Không đổi câu hỏi.
Không tăng progress UI.
Giữ nguyên textarea hoặc cho user nhập lại.
Cho user gửi lại câu trả lời đúng trọng tâm hơn.

Ví dụ:

if (data.assistant_message?.message_type === "answer_warning") {
  setWarning(data.assistant_message.content);
  return;
}
Case 2: Câu trả lời hợp lệ và bài test tiếp tục

Response:

{
  "status": "in_progress",
  "session": {
    "session_id": "uuid",
    "student_id": "uuid",
    "status": "in_progress",
    "current_step": 2,
    "scores": {
      "R": 0.5,
      "I": 2,
      "A": 1,
      "S": 0,
      "E": 0,
      "C": 0.5
    },
    "confidence": {
      "R": 0.2,
      "I": 0.8,
      "A": 0.4,
      "S": 0,
      "E": 0,
      "C": 0.2
    },
    "riasec_code": "IAC"
  },
  "user_message": {
    "message_type": "answer",
    "content": "Em thích phân tích dữ liệu..."
  },
  "assistant_message": {
    "message_type": "adaptive_scenario",
    "content": "Một CLB cần mở rộng thành viên nhưng nguồn lực hạn chế...",
    "metadata_json": {
      "type": "adaptive_scenario",
      "focus_groups": ["I", "A"],
      "context": "hoạt động CLB học thuật",
      "question_style": "resource_constraint"
    }
  },
  "dcp_id": null
}
FE xử lý khi tiếp tục
Clear warning.
Clear textarea.
Update current_step.
Update scores.
Hiển thị assistant_message.content làm câu hỏi tiếp theo.
Case 3: Bài test hoàn tất

Sau tối đa 7 câu trả lời hợp lệ hoặc khi đủ độ tin cậy, response:

{
  "status": "completed",
  "session": {
    "session_id": "uuid",
    "status": "completed",
    "current_step": 7,
    "riasec_code": "IAC",
    "termination_reason": "Reached maximum number of questions"
  },
  "user_message": {
    "message_type": "answer",
    "content": "..."
  },
  "assistant_message": {
    "message_type": "final_result",
    "content": "Bài đánh giá đã hoàn tất. Mã RIASEC của bạn là IAC..."
  },
  "dcp_id": "uuid"
}
FE xử lý khi completed
Lưu dcp_id.
Chuyển sang màn kết quả.
Gọi API lấy chi tiết profile:
GET /profiles/{dcp_id}
8. API lấy kết quả RIASEC profile
Mục đích

Lấy kết quả cuối cùng của bài đánh giá.

Endpoint
GET /profiles/{dcp_id}

Full URL:

http://localhost:8002/api/riasec/profiles/{dcp_id}
Path params
Param	Type	Required	Mô tả
dcp_id	UUID	Yes	ID kết quả cuối từ response completed
Response thành công
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
  "career_groups": [
    "Công nghệ thông tin",
    "Khoa học dữ liệu",
    "AI",
    "Thiết kế",
    "Truyền thông"
  ],
  "digital_competencies": {
    "I": [
      "Phân tích dữ liệu",
      "Tư duy logic",
      "Tìm kiếm và đánh giá thông tin"
    ],
    "A": [
      "Sáng tạo nội dung số",
      "Thiết kế trải nghiệm"
    ],
    "C": [
      "Quản lý dữ liệu",
      "Tự động hóa quy trình"
    ]
  },
  "recommended_majors": [
    "Công nghệ thông tin",
    "Khoa học dữ liệu",
    "Trí tuệ nhân tạo",
    "Thiết kế UX/UI",
    "Hệ thống thông tin"
  ],
  "summary": "Kết quả hiện tại cho thấy bạn nổi bật ở nhóm IAC..."
}
FE nên hiển thị
Mã RIASEC.
Biểu đồ điểm R, I, A, S, E, C.
Summary.
Nhóm ngành phù hợp.
Ngành học gợi ý.
Năng lực số nên phát triển.
9. TypeScript types gợi ý
export type RiasecGroup = "R" | "I" | "A" | "S" | "E" | "C";

export type RiasecScore = Record<RiasecGroup, number>;

export type RiasecStatus = "in_progress" | "completed" | "abandoned";

export interface RiasecSession {
  session_id: string;
  student_id: string;
  status: RiasecStatus;
  current_step: number;
  scores: RiasecScore;
  confidence: RiasecScore;
  riasec_code?: string | null;
  termination_reason?: string | null;
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
  metadata_json?: {
    type?: string;
    focus_groups?: RiasecGroup[];
    context?: string;
    question_style?: string;
    reason?: string;
    repeat_question?: string;
    [key: string]: unknown;
  };
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
10. Axios service gợi ý
import axios from "axios";

export const profileApi = axios.create({
  baseURL: import.meta.env.VITE_PROFILE_API_URL,
});

export const riasecApi = axios.create({
  baseURL: import.meta.env.VITE_RIASEC_API_URL,
});

export async function registerStudent(payload: {
  full_name: string;
  email: string;
  password: string;
  province?: string;
  area_code?: string;
  dob?: string;
  priority_group?: string;
  target_province?: string;
}) {
  const res = await profileApi.post("/auth/register", payload);
  return res.data;
}

export async function getMe() {
  const token = localStorage.getItem("access_token");

  const res = await profileApi.get("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return res.data;
}

export async function startRiasecSession(studentId: string) {
  const res = await riasecApi.post("/sessions", {
    student_id: studentId,
  });

  return res.data;
}

export async function submitRiasecAnswer(
  sessionId: string,
  answerText: string
) {
  const res = await riasecApi.post(`/sessions/${sessionId}/answers`, {
    answer_text: answerText,
  });

  return res.data;
}

export async function getRiasecProfile(dcpId: string) {
  const res = await riasecApi.get(`/profiles/${dcpId}`);
  return res.data;
}
11. UI behavior bắt buộc
Khi bắt đầu test

FE gọi:

startRiasecSession(studentId)

Sau đó hiển thị:

response.question.content
Khi gửi câu trả lời

FE gọi:

submitRiasecAnswer(sessionId, answerText)

Nếu response là warning:

if (data.assistant_message?.message_type === "answer_warning") {
  setWarning(data.assistant_message.content);
  return;
}

Nếu tiếp tục:

setQuestion(data.assistant_message.content);
setStep(data.session.current_step);

Nếu completed:

setDcpId(data.dcp_id);
navigate(`/riasec/result/${data.dcp_id}`);
Khi xem kết quả

FE gọi:

getRiasecProfile(dcpId)

Render:

riasec_code
scores
confidence
career_groups
recommended_majors
digital_competencies
summary
12. Progress UI

Bài test tối đa 7 câu trả lời hợp lệ.

FE nên hiển thị:

Câu current_step + 1 / 7

Lưu ý:

current_step là số câu hợp lệ đã trả lời.
Nếu user trả lời sai/lạc đề, current_step không tăng.
Khi status = completed, không cho submit tiếp.

Ví dụ:

const displayStep = Math.min(session.current_step + 1, 7);
13. Checklist FE
[ ] Có màn đăng ký / đăng nhập
[ ] Lưu access_token
[ ] Lưu student_id
[ ] Có màn bắt đầu RIASEC
[ ] Gọi POST /sessions
[ ] Hiển thị anchor question
[ ] Gửi answer qua POST /sessions/{session_id}/answers
[ ] Xử lý answer_warning
[ ] Không tăng step khi warning
[ ] Hiển thị adaptive question tiếp theo
[ ] Khi completed thì lưu dcp_id
[ ] Gọi GET /profiles/{dcp_id}
[ ] Render mã RIASEC
[ ] Render biểu đồ scores
[ ] Render ngành học gợi ý
[ ] Render summary