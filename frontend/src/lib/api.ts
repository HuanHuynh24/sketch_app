export type RiasecGroup = "R" | "I" | "A" | "S" | "E" | "C";

export type RiasecScore = Record<RiasecGroup, number>;

export type RiasecStatus = "in_progress" | "completed" | "abandoned";

export interface Student {
  student_id: string;
  full_name: string;
  email: string;
  dob?: string | null;
  province: string;
  area_code: string;
  priority_group?: string | null;
  target_province?: string | null;
  is_active?: boolean;
  is_verified?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  student: Student;
}

export interface RegisterStudentPayload {
  full_name: string;
  email: string;
  password: string;
  province: string;
  area_code: string;
  dob?: string;
  priority_group?: string;
  target_province?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RiasecSession {
  session_id: string;
  student_id: string;
  status: RiasecStatus;
  current_step: number;
  min_steps?: number;
  max_steps?: number;
  scores: RiasecScore;
  confidence: RiasecScore;
  entropy?: number;
  current_focus_groups?: RiasecGroup[];
  riasec_code?: string | null;
  termination_reason?: string | null;
  final_summary?: string | null;
  created_at?: string;
  updated_at?: string;
  completed_at?: string | null;
}

export interface RiasecMessage {
  message_id: string;
  session_id: string;
  role: "assistant" | "user" | "system" | string;
  content: string;
  message_type:
    | "anchor_scenario"
    | "adaptive_scenario"
    | "answer"
    | "invalid_answer"
    | "answer_warning"
    | "final_result"
    | string;
  metadata_json?: {
    type?: string;
    focus_groups?: RiasecGroup[];
    context?: string;
    question_style?: string;
    reason?: string;
    repeat_question?: string;
    [key: string]: unknown;
  } | null;
  riasec_signal?: Record<string, unknown> | null;
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

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

const profileApiUrl =
  process.env.NEXT_PUBLIC_PROFILE_API_URL ?? "http://localhost:8000/api/profile";

const riasecApiUrl =
  process.env.NEXT_PUBLIC_RIASEC_API_URL ?? "http://localhost:8000/api/riasec";

const STORAGE_KEYS = {
  token: "access_token",
  studentId: "student_id",
} as const;

function trimTrailingSlash(url: string) {
  return url.replace(/\/+$/, "");
}

function endpoint(baseUrl: string, path: string) {
  return `${trimTrailingSlash(baseUrl)}${path.startsWith("/") ? path : `/${path}`}`;
}

function getErrorMessage(status: number, payload: unknown) {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;

    if (typeof detail === "string") {
      if (detail === "Email already exists") {
        return "Email này đã được sử dụng. Vui lòng đăng nhập hoặc dùng email khác.";
      }

      if (detail === "Invalid email or password") {
        return "Email hoặc mật khẩu không đúng.";
      }

      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            return String((item as { msg: unknown }).msg);
          }

          return String(item);
        })
        .join(" ");
    }
  }

  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  return `Yêu cầu thất bại với mã lỗi ${status}.`;
}

async function requestJson<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  console.log(`Requesting ${url} with options:`, options);
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    throw new ApiError(getErrorMessage(response.status, payload), response.status, payload);
  }

  return payload as T;
}

function getBrowserStorage() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage;
}

export function saveAuthSession(response: AuthResponse) {
  const storage = getBrowserStorage();

  if (!storage) {
    return;
  }

  storage.setItem(STORAGE_KEYS.token, response.access_token);
  storage.setItem(STORAGE_KEYS.studentId, response.student.student_id);
}

export function clearAuthSession() {
  const storage = getBrowserStorage();

  if (!storage) {
    return;
  }

  storage.removeItem(STORAGE_KEYS.token);
  storage.removeItem(STORAGE_KEYS.studentId);
}

export function getAccessToken() {
  return getBrowserStorage()?.getItem(STORAGE_KEYS.token) ?? null;
}

export function getStudentId() {
  return getBrowserStorage()?.getItem(STORAGE_KEYS.studentId) ?? null;
}

export function saveStudentId(studentId: string) {
  getBrowserStorage()?.setItem(STORAGE_KEYS.studentId, studentId);
}

export async function registerStudent(payload: RegisterStudentPayload) {
  console.log("Logging in with payload:", payload);
  return requestJson<AuthResponse>(endpoint(profileApiUrl, "/auth/register"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function loginStudent(payload: LoginPayload) {
  return requestJson<AuthResponse>(endpoint(profileApiUrl, "/auth/login"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMe() {
  const token = getAccessToken();
  return requestJson<Student>(endpoint(profileApiUrl, "/auth/me"), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

export async function startRiasecSession(studentId: string) {
  const token = getAccessToken();
  return requestJson<StartRiasecResponse>(endpoint(riasecApiUrl, "/sessions"), {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: JSON.stringify({
      student_id: studentId,
    }),
  });
}

export async function submitRiasecAnswer(sessionId: string, answerText: string) {
  const token = getAccessToken();
  return requestJson<SubmitAnswerResponse>(
    endpoint(riasecApiUrl, `/sessions/${sessionId}/answers`),
    {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: JSON.stringify({
        answer_text: answerText,
      }),
    },
  );
}

export async function getRiasecProfile(dcpId: string) {
  const token = getAccessToken();
  return requestJson<DigitalCompetencyProfile>(
    endpoint(riasecApiUrl, `/profiles/${dcpId}`),{
      method: "GET",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }
  );
}
