# FE API Guide

Tài liệu này dành cho frontend dev tích hợp luồng hồ sơ học sinh, RIASEC và gợi ý trường đại học.

FE chỉ gọi qua API Gateway:

```txt
http://localhost:8000
```

Không gọi trực tiếp các service nội bộ từ FE.

## 1. Base Config

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

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

## 2. Auth

### Register

```txt
POST /api/profile/auth/register
```

Request:

```json
{
  "full_name": "Nguyen Van A",
  "email": "student@example.com",
  "password": "123456",
  "province": "TP.HCM",
  "area_code": "KV2",
  "dob": "2007-05-20",
  "priority_group": "01",
  "target_province": "TP.HCM",
  "target_country": "Vietnam",
  "target_budget": 15000000
}
```

Response gồm `access_token`, `token_type`, `expires_in`, `student`.

FE lưu:

```ts
localStorage.setItem("access_token", data.access_token);
localStorage.setItem("student", JSON.stringify(data.student));
```

### Login

```txt
POST /api/profile/auth/login
```

Request:

```json
{
  "email": "student@example.com",
  "password": "123456"
}
```

### Get Current User

```txt
GET /api/profile/auth/me
Authorization: Bearer ACCESS_TOKEN
```

## 3. Profile & Academic Record

### Get My Profile

```txt
GET /api/profile/students/me
Authorization: Bearer ACCESS_TOKEN
```

### Update My Profile

```txt
PATCH /api/profile/students/me
Authorization: Bearer ACCESS_TOKEN
```

Request, chỉ gửi field cần sửa:

```json
{
  "target_country": "Vietnam",
  "target_province": "TP.HCM",
  "target_budget": 15000000
}
```

### Upsert Academic Record

```txt
PUT /api/profile/students/me/academic-record
Authorization: Bearer ACCESS_TOKEN
```

Request:

```json
{
  "score_math": 8,
  "score_literature": 6,
  "optional_subject_1": "Hóa học",
  "score_optional_1": 8,
  "optional_subject_2": "Vật lý",
  "score_optional_2": 8.5,
  "exam_year": 2026,
  "ielts_score": 6,
  "toeic_score": 0
}
```

Validation:

- Điểm môn học: `0..10`
- IELTS: `0..9`
- TOEIC: `0..990`
- `optional_subject_1` và `optional_subject_2` không được trùng nhau.

### Get Academic Record

```txt
GET /api/profile/students/me/academic-record
Authorization: Bearer ACCESS_TOKEN
```

## 4. RIASEC Flow

Flow FE chuẩn:

```txt
1. Login/register, lấy access_token.
2. Update profile mục tiêu học tập nếu cần.
3. Upsert academic record.
4. POST /api/riasec/sessions để bắt đầu bài RIASEC.
5. POST /api/riasec/sessions/{session_id}/answers cho từng câu trả lời.
6. Khi status = completed, lấy dcp_id.
7. POST /api/rag/search/universities với dcp_id để sinh gợi ý trường.
8. GET /api/admission/recommendations/students/{student_id} để xem lại kết quả đã lưu.
```

### Start RIASEC Session

```txt
POST /api/riasec/sessions
Authorization: Bearer ACCESS_TOKEN
```

Không gửi body.

### Submit RIASEC Answer

```txt
POST /api/riasec/sessions/{session_id}/answers
Authorization: Bearer ACCESS_TOKEN
```

Request:

```json
{
  "answer_text": "Em sẽ phân tích nhu cầu trước, sau đó chọn hướng trình bày phù hợp..."
}
```

`answer_text`: 1 đến 3000 ký tự.

Nếu response có `assistant_message.message_type === "answer_warning"` thì FE không tăng progress.

Khi hoàn tất, response có:

```json
{
  "status": "completed",
  "dcp_id": "f3a6a704-80c2-4c83-b59a-4b4cb0681178"
}
```

### Get RIASEC Profile

```txt
GET /api/riasec/profiles/{dcp_id}
Authorization: Bearer ACCESS_TOKEN
```

## 5. Generate University Recommendations

Endpoint này gọi RAG, lấy profile + academic record + RIASEC, search trong pgvector, rồi lưu kết quả vào `admission.university_recommendations`.

```txt
POST /api/rag/search/universities
Authorization: Bearer ACCESS_TOKEN
```

Request production:

```json
{
  "dcp_id": "f3a6a704-80c2-4c83-b59a-4b4cb0681178"
}
```

Yêu cầu:

- Bắt buộc có `Authorization` khi chỉ gửi `dcp_id`.
- Học sinh phải có profile và academic record.
- `dcp_id` phải thuộc đúng học sinh đang đăng nhập.

Request test không cần token:

```json
{
  "override_profile": {
    "student_id": "00000000-0000-0000-0000-000000000001",
    "target_country": "Vietnam",
    "target_province": "TP.HCM",
    "target_budget": 15000000,
    "score_math": 8,
    "score_literature": 6,
    "optional_subject_1": "Hóa học",
    "score_optional_1": 8,
    "optional_subject_2": "Vật lý",
    "score_optional_2": 8.5,
    "ielts_score": 6,
    "toeic_score": 0
  },
  "override_riasec": {
    "riasec_code": "ECI",
    "career_groups": ["Kinh doanh", "Marketing", "Công nghệ thông tin"],
    "recommended_majors": [
      "Quản trị kinh doanh",
      "Marketing",
      "Tài chính ngân hàng",
      "Công nghệ thông tin"
    ]
  }
}
```

Response chính:

```json
{
  "query_used": {
    "optimized_query": "Tuyển sinh ngành Quản trị kinh doanh, Marketing...",
    "target_countries": ["Vietnam"],
    "target_majors": ["Quản trị kinh doanh", "Marketing"],
    "budget_limit_usd": 600,
    "min_ielts": 6,
    "keywords": ["học bổng", "học phí", "điều kiện xét tuyển"]
  },
  "results_count": 10,
  "is_background_crawling": false,
  "saved_recommendations_count": 10,
  "recommendations": [
    {
      "id": "recommendation_uuid",
      "student_id": "student_uuid",
      "logo": [
        "https://tuyensinhso.vn/include/elfinder/../../images/files/tuyensinhso.com/truong-dai-hoc-a.jpg"
      ],
      "description": "Loại trường: Dân lập; Địa chỉ: Khu đô thị công nghệ FPT Đà Nẵng, Phường Ngũ Hành Sơn, TP. Đà Nẵng.",
      "content": {
        "overview": "Tổng quan gợi ý...",
        "document": {
          "format": "html",
          "source_path": "da-nang/dai-hoc-fpt-da-nang.md",
          "markdown": "# Đại học FPT Đà Nẵng\n\nToàn bộ nội dung markdown gốc...",
          "html": "<h1>Đại học FPT Đà Nẵng</h1><p>Toàn bộ nội dung đã format HTML...</p>"
        },
        "matched_context": "Đoạn markdown liên quan được match từ pgvector...",
        "career_opportunities": ["Business Analyst", "Marketing Executive"],
        "tuition_fee": {
          "value": null,
          "currency": null,
          "display": null
        },
        "admission_method": {
          "student_scores": {
            "math": 8,
            "literature": 6,
            "optional_subject_1": "Hóa học",
            "score_optional_1": 8,
            "optional_subject_2": "Vật lý",
            "score_optional_2": 8.5,
            "ielts": 6,
            "toeic": 0
          }
        },
        "advantages": [
          "Country matches the student's target country.",
          "Strong semantic match in the university knowledge base."
        ],
        "riasec": {
          "code": "ECI",
          "recommended_majors": ["Quản trị kinh doanh", "Marketing"],
          "career_groups": ["Kinh doanh", "Marketing"]
        },
        "source": {
          "url": "da-nang/dai-hoc-fpt-da-nang.md",
          "path": "da-nang/dai-hoc-fpt-da-nang.md",
          "country": "Vietnam",
          "city": "da-nang",
          "similarity_score": 0.21
        }
      },
      "type": 0,
      "name_universities": "Đại học FPT Đà Nẵng",
      "name_majors": "Quản trị kinh doanh",
      "updated_at": "2026-05-18T10:00:00Z"
    }
  ],
  "data": {
    "domestic": [],
    "foreign": []
  }
}
```

Business rule:

- Trả tối đa 5 trường trong nước và 5 trường ngoài nước.
- `type = 0`: trường trong nước.
- `type = 1`: trường ngoài nước.
- `logo` là mảng hình ảnh/gallery lấy từ markdown. Tên field là `logo` nhưng FE nên hiểu là `images`.
- `description` là text ngắn cho card preview. FE không cần tự build lại.
- `content.document.markdown` là toàn bộ file markdown gốc của trường.
- `content.document.html` là HTML render sẵn từ markdown để FE hiển thị trang chi tiết.
- `content.matched_context` là chunk được pgvector match, chỉ nên dùng để debug hoặc giải thích match.

## 6. Get Saved Recommendations

Dùng API này khi FE reload trang kết quả hoặc muốn xem lại recommendation đã sinh trước đó.

```txt
GET /api/admission/recommendations/students/{student_id}
```

Response là danh sách `UniversityRecommendation`, cùng contract với `recommendations` ở endpoint RAG.

Lưu ý bảo mật hiện tại:

- API này nhận `student_id` trên path.
- FE chỉ nên gọi với `student.student_id` của user đang đăng nhập.
- Nếu sau này cần bảo mật chặt hơn, backend nên thêm auth guard cho endpoint này.

## 7. Frontend Rendering Notes

### Recommendation Card

Field nên dùng:

```ts
const image = item.logo?.[0];
const title = item.name_universities;
const major = item.name_majors;
const typeLabel = item.type === 0 ? "Trong nước" : "Ngoài nước";
const description = item.description;
```

Không dùng ảnh của item đầu tiên cho toàn bộ card. Luôn dùng:

```ts
item.logo?.[0]
```

### Recommendation Detail

Field nên render:

```ts
item.logo                         // gallery images
item.description                  // card preview text
item.content.document.html        // full source markdown rendered as HTML
item.content.document.markdown    // full source markdown, optional fallback/debug
item.content.overview
item.content.advantages
item.content.admission_method
item.content.tuition_fee
item.content.career_opportunities
item.content.riasec
item.content.source
item.content.matched_context      // optional/debug/source chunk
```

FE nên render detail bằng `item.content.document.html`. Vì HTML này do backend sinh từ markdown nội bộ, FE có thể render bằng `dangerouslySetInnerHTML`, nhưng không trộn thêm HTML từ input người dùng vào cùng container.

### Group Domestic/Foreign

```ts
const domestic = recommendations.filter((item) => item.type === 0);
const foreign = recommendations.filter((item) => item.type === 1);
```

## 8. TypeScript Types

```ts
export interface UniversityRecommendation {
  id: string;
  student_id: string;
  logo: string[];
  description: string;
  content: {
    overview?: string;
    document?: {
      format: "html";
      source_path?: string | null;
      markdown: string;
      html: string;
    };
    matched_context?: string;
    career_opportunities?: string[];
    tuition_fee?: {
      value?: number | null;
      currency?: string | null;
      display?: string | null;
    };
    admission_method?: Record<string, unknown>;
    advantages?: string[];
    riasec?: Record<string, unknown>;
    source?: Record<string, unknown>;
    [key: string]: unknown;
  };
  type: 0 | 1;
  name_universities: string;
  name_majors: string;
  updated_at: string;
}

export interface RagSearchResponse {
  query_used: {
    optimized_query: string;
    target_countries: string[];
    target_majors: string[];
    budget_limit_usd: number | null;
    min_ielts: number | null;
    keywords: string[];
  };
  results_count: number;
  is_background_crawling: boolean;
  saved_recommendations_count: number;
  recommendations: UniversityRecommendation[];
  data: {
    domestic: unknown[];
    foreign: unknown[];
  };
}
```

## 9. Error Handling

Các lỗi thường gặp:

```txt
400: Request không hợp lệ hoặc internal service trả lỗi.
401: Thiếu token, token sai hoặc token hết hạn.
403: Không có quyền truy cập resource.
404: Không tìm thấy profile, academic record, session hoặc dcp.
422: Body không đúng JSON/schema.
429: Gemini API hết quota/spending cap.
500: Lỗi server.
502/504: Gateway hoặc service nội bộ lỗi/timeout.
```

`422 JSON decode error` thường do body Swagger không phải JSON hợp lệ, ví dụ dấu phẩy thừa:

```json
{
  "dcp_id": "uuid",
}
```

Body đúng:

```json
{
  "dcp_id": "uuid"
}
```

## 10. API Không Dành Cho FE

Không gọi từ FE:

```txt
POST /api/admission/recommendations/bulk
POST /api/rag/ingestion/documents
```

Các API này dành cho backend/admin/devops:

- `POST /api/rag/ingestion/documents`: dùng khi thêm/sửa markdown trong `backend/data`.
- `POST /api/admission/recommendations/bulk`: RAG service gọi nội bộ để replace recommendation.

Khi sửa file markdown trong `backend/data`, dữ liệu không tự embedding lại ngay. Cần gọi ingestion để refresh `rag.document_chunks`; sau đó gọi search để replace recommendation đã lưu.
