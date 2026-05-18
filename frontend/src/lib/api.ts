import axios, { AxiosHeaders } from "axios";
import type { AxiosRequestConfig } from "axios";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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

type ApiRequestConfig = Omit<AxiosRequestConfig, "auth"> & {
  auth?: boolean;
};

const STORAGE_KEYS = {
  token: "access_token",
  student: "student",
  legacyStudentId: "student_id",
} as const;

const apiClient = axios.create({
  baseURL: API_BASE_URL.replace(/\/+$/, ""),
  timeout: 30000,
});

function getBrowserStorage() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage;
}

function isFormData(value: unknown) {
  return typeof FormData !== "undefined" && value instanceof FormData;
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

      if (detail === "Session is not in progress") {
        return "Bài đánh giá đã hoàn tất. Hãy xem kết quả hoặc bắt đầu lại.";
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

    return JSON.stringify(detail);
  }

  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  return `Yêu cầu thất bại với mã lỗi ${status}.`;
}

function toApiError(error: unknown) {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status ?? 0;
    const detail = error.response?.data ?? error.message;
    const message =
      status > 0
        ? getErrorMessage(status, detail)
        : "Không thể kết nối tới hệ thống. Vui lòng kiểm tra backend và thử lại.";

    return new ApiError(message, status, detail);
  }

  if (error instanceof ApiError) {
    return error;
  }

  return new ApiError("Không thể xử lý phản hồi từ hệ thống.", 0, error);
}

async function apiRequest<T>(
  path: string,
  options: ApiRequestConfig = {},
): Promise<T> {
  const { auth, headers: initialHeaders, data, ...axiosOptions } = options;
  const headers = AxiosHeaders.from(initialHeaders as AxiosHeaders | undefined);

  if (data !== undefined && !isFormData(data) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (auth) {
    const token = getAccessToken();

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  try {
    const response = await apiClient.request<T>({
      ...axiosOptions,
      url: path,
      data,
      headers,
    });

    return response.data;
  } catch (error) {
    throw toApiError(error);
  }
}

export function saveAuthSession(response: AuthResponse) {
  const storage = getBrowserStorage();

  if (!storage) {
    return;
  }

  storage.setItem(STORAGE_KEYS.token, response.access_token);
  storage.setItem(STORAGE_KEYS.student, JSON.stringify(response.student));
  storage.removeItem(STORAGE_KEYS.legacyStudentId);
}

export function saveStudent(student: Student) {
  getBrowserStorage()?.setItem(STORAGE_KEYS.student, JSON.stringify(student));
}

export function clearAuthSession() {
  const storage = getBrowserStorage();

  if (!storage) {
    return;
  }

  storage.removeItem(STORAGE_KEYS.token);
  storage.removeItem(STORAGE_KEYS.student);
  storage.removeItem(STORAGE_KEYS.legacyStudentId);
}

export function getAccessToken() {
  return getBrowserStorage()?.getItem(STORAGE_KEYS.token) ?? null;
}

export function getStoredStudent() {
  const rawStudent = getBrowserStorage()?.getItem(STORAGE_KEYS.student);

  if (!rawStudent) {
    return null;
  }

  try {
    return JSON.parse(rawStudent) as Student;
  } catch {
    return null;
  }
}

export async function registerStudent(payload: RegisterStudentPayload) {
  const data = await apiRequest<AuthResponse>("/api/profile/auth/register", {
    method: "POST",
    data: payload,
  });

  saveAuthSession(data);
  return data;
}

export async function loginStudent(payload: LoginPayload) {
  const data = await apiRequest<AuthResponse>("/api/profile/auth/login", {
    method: "POST",
    data: payload,
  });

  saveAuthSession(data);
  return data;
}

export async function getMe() {
  const student = await apiRequest<Student>("/api/profile/auth/me", {
    method: "GET",
    auth: true,
  });

  saveStudent(student);
  return student;
}

export async function startRiasecSession() {
  return apiRequest<StartRiasecResponse>("/api/riasec/sessions", {
    method: "POST",
    auth: true,
  });
}

export async function submitRiasecAnswer(sessionId: string, answerText: string) {
  return apiRequest<SubmitAnswerResponse>(
    `/api/riasec/sessions/${sessionId}/answers`,
    {
      method: "POST",
      auth: true,
      data: {
        answer_text: answerText,
      },
    },
  );
}

export async function getRiasecProfile(dcpId: string) {
  return apiRequest<DigitalCompetencyProfile>(`/api/riasec/profiles/${dcpId}`, {
    method: "GET",
    auth: true,
  });
}

export async function getLatestRiasecProfile() {
  return apiRequest<DigitalCompetencyProfile>("/api/riasec/profiles/latest", {
    method: "GET",
    auth: true,
  });
}
