
TÀI LIỆU PHÂN TÍCH HỆ THỐNG

Hệ thống tư vấn hướng nghiệp & dự đoán tuyển sinh AI


Dành cho học sinh Trung học Phổ thông Việt Nam




# 1. Tổng quan hệ thống

## 1.1 Bài toán

Học sinh THPT Việt Nam đang đối mặt với hai bài toán chưa được giải quyết tốt: không có công cụ đánh giá sở thích nghề nghiệp cá nhân hóa, và không thể dự đoán khả năng đỗ đại học dựa trên hồ sơ thực tế của bản thân. Tư vấn truyền thống phụ thuộc vào giáo viên, thiếu dữ liệu, và không thể cá nhân hóa cho từng học sinh.


## 1.2 Mục tiêu hệ thống

Đánh giá sở thích nghề nghiệp theo mô hình Holland RIASEC thông qua hội thoại AI tự nhiên

Xây dựng hồ sơ năng lực số (DCP) cá nhân hóa và gợi ý nhóm ngành nghề phù hợp

Dự đoán điểm chuẩn từng ngành từng trường dựa trên dữ liệu lịch sử

Phân nhóm trường theo 3 mức độ rủi ro: An toàn, Cân bằng, Thử thách

Cung cấp thông tin chi tiết học phí, học bổng, chỉ tiêu qua RAG pipeline


## 1.3 Luồng 3 bước thống nhất

Toàn bộ hệ thống được tổ chức thành một luồng tuyến tính, đầu ra của bước trước là đầu vào của bước sau:



# 2. Kiến trúc tổng thể (High-level Architecture)

Hệ thống được tổ chức theo kiến trúc layered 4 tầng. Mỗi tầng có trách nhiệm rõ ràng và chỉ giao tiếp với tầng liền kề.


TẦNG 1 — CLIENT LAYER


▼  HTTPS / REST API


TẦNG 2 — API GATEWAY


▼  Internal HTTP


TẦNG 3 — CORE SERVICES LAYER


▼  DB Queries / Model Calls


TẦNG 4 — DATA LAYER


## 2.1 Tích hợp bên ngoài


## 2.2 Công nghệ sử dụng


# 3. System Design — Luồng dữ liệu chi tiết

## 3.1 Luồng Phân hệ 1 — RIASEC Assessment

Học sinh điền form → Profile Service lưu student_profile vào PostgreSQL

Frontend gọi POST /riasec/sessions → RIASEC Service khởi tạo session, trả về câu hỏi 1

Học sinh trả lời → POST /riasec/sessions/{id}/messages → LangChain gọi GPT-4o-mini sinh câu hỏi tiếp

Sau mỗi câu trả lời: cập nhật session state, kiểm tra điều kiện dừng

Khi dừng: trigger async job → GPT-4o đọc toàn bộ hội thoại, chấm điểm RIASEC, xuất DCP

DCP lưu vào bảng digital_competency_profiles → trả dcp_id về frontend

Frontend render radar chart + danh sách ngành nghề gợi ý


## 3.2 Luồng Phân hệ 2 — Dự đoán tuyển sinh

Admission Service đọc DCP (lấy top_groups) và student_profile (lấy điểm thi)

Lọc danh sách ngành-trường theo top_groups và khu vực mong muốn

Với mỗi cặp (ngành, trường, tổ hợp môn): gọi XGBoost model dự đoán điểm chuẩn

So sánh điểm học sinh với điểm chuẩn dự đoán → phân nhóm An toàn / Cân bằng / Thử thách

Với mỗi trường trong danh sách: gọi RAG Service lấy thông tin học phí, học bổng, chỉ tiêu

Tổng hợp và trả kết quả về frontend


## 3.3 Luồng RAG Service

Đề án tuyển sinh PDF được load vào hệ thống → chunking theo đoạn văn

Mỗi chunk được embedding bằng text-embedding-ada-002 → lưu vào Vector DB

Khi có query: hybrid search (BM25 keyword + vector similarity) → lấy top-K chunk liên quan

Top-K chunk + câu hỏi → GPT-4o → câu trả lời chính xác có trích dẫn nguồn


# 4. Thiết kế Database

Hệ thống sử dụng PostgreSQL làm database chính với 10 bảng, tổ chức thành 3 nhóm theo phạm vi chức năng.


Nhóm 0 — Dùng chung

### 4.1 Bảng students

Lưu thông tin cơ bản của học sinh. Đây là bảng gốc, tất cả bảng khác đều liên kết về đây.



### 4.2 Bảng student_academic_records

Lưu điểm học bạ và điểm thi của học sinh.



Nhóm 1 — Phân hệ 1: RIASEC Assessment

### 4.3 Bảng riasec_sessions

Quản lý mỗi phiên đánh giá RIASEC. Một học sinh có thể làm lại nhiều lần.



### 4.4 Bảng conversation_messages

Lưu từng lượt hội thoại. Toàn bộ bảng này được đưa vào context khi chấm điểm.



### 4.5 Bảng digital_competency_profiles

Kết quả DCP cuối cùng — đầu ra của Phân hệ 1, đầu vào của Phân hệ 2.



Nhóm 2 — Phân hệ 2: Dự đoán tuyển sinh

### 4.6 Bảng admission_scores_history

Dữ liệu điểm chuẩn lịch sử — nguồn huấn luyện chính của XGBoost model.



### 4.7 Bảng admission_predictions

Lưu kết quả dự đoán điểm chuẩn theo từng chu kỳ. Dùng để tra cứu nhanh, tránh gọi model lại.



### 4.8 Bảng universities

Thông tin cơ bản của các trường đại học trong hệ thống.



### 4.9 Bảng majors

Thông tin ngành học và mapping sang mã RIASEC.



### 4.10 Bảng student_recommendations

Lưu kết quả tư vấn tuyển sinh cho từng học sinh — đầu ra cuối cùng của toàn hệ thống.



# 5. API Endpoints

Tất cả endpoint có base URL /api/v1. Xác thực bằng Bearer JWT token trong header Authorization. Response format: JSON.


💡 Prefix: PH1 = /riasec  |  PH2 = /admission  |  RAG = /rag  |  Auth = /auth


5.0 Authentication


### POST /auth/register — Đăng ký tài khoản


### POST /auth/login — Đăng nhập


5.1 Phân hệ 1 — RIASEC Assessment


### POST /riasec/sessions — Khởi tạo phiên đánh giá


### POST /riasec/sessions/{id}/messages — Gửi câu trả lời


### GET /riasec/sessions/{id} — Trạng thái phiên


### GET /riasec/profiles/{dcp_id} — Lấy kết quả DCP


### PATCH /riasec/sessions/{id}/abandon — Từ bỏ phiên


5.2 Phân hệ 2 — Dự đoán tuyển sinh


### POST /admission/recommend — Tạo tư vấn tuyển sinh


### GET /admission/predict — Dự đoán điểm chuẩn


### GET /admission/history — Lịch sử điểm chuẩn


### GET /admission/recommendations/{id} — Lấy kết quả tư vấn


5.3 RAG Service — Hỏi đáp tuyển sinh


### POST /rag/query — Hỏi đáp thông tin tuyển sinh


# 6. Thiết kế mô hình Machine Learning

## 6.1 Bài toán & chiến lược

Mỗi ngành mỗi trường chỉ có 5–8 điểm dữ liệu lịch sử — quá ít để train model riêng lẻ. Chiến lược là pool toàn bộ dữ liệu của tất cả ngành tất cả trường thành một dataset duy nhất. Model học pattern chung về biến động điểm chuẩn, áp dụng cho từng ngành cụ thể thông qua các feature định danh.


## 6.2 Features đầu vào


## 6.3 Mô hình & đánh giá


💡 Đánh giá bằng k-fold cross-validation (k=5), split theo năm để tránh data leakage: train trên năm 2014–2022, test trên 2023.


# 7. Tích hợp LLM

## 7.1 Tổng quan — 3 điểm gọi LLM


## 7.2 System prompt — Hội thoại RIASEC

System prompt được chia 4 block theo thứ tự ưu tiên từ trên xuống:

Block 1 — Vai trò: chuyên gia tư vấn hướng nghiệp, ẩn thông tin đang dùng RIASEC

Block 2 — 60 câu O*NET Short Form có nhãn R/I/A/S/E/C làm bộ tham chiếu

Block 3 — Quy tắc sinh tình huống: ngữ cảnh THPT VN, hỏi sở thích hoạt động không hỏi tính cách

Block 4 — Quy tắc dừng và format JSON output cố định


## 7.3 System prompt — Chấm điểm RIASEC

Toàn bộ conversation_history được đưa vào context. Model thực hiện 3 lớp phân tích:

Lớp 1: map từng câu trả lời về nhóm RIASEC dựa trên 60 câu O*NET tham chiếu

Lớp 2: kiểm tra tính nhất quán — signal xuất hiện nhiều lần có trọng số cao hơn

Lớp 3: chuẩn hóa điểm 6 nhóm thành phần trăm, xác định top_groups, viết reasoning

💡 Output JSON bắt buộc: { scores:{R,I,A,S,E,C}, top_groups:[], confidence:float, reasoning:string }


## 7.4 Điều kiện dừng hội thoại


# 8. Tích hợp giữa hai phân hệ

## 8.1 Điểm kết nối — Smart Matching

Phân hệ 2 đọc trực tiếp DCP từ Phân hệ 1 thông qua internal API call. Quy trình kết nối:

Đọc top_groups từ DCP (ví dụ: ['R','I'])

Query bảng majors để lấy danh sách major_code có riasec_mapping chứa R hoặc I

Join với bảng admission_predictions để lấy điểm chuẩn dự đoán của từng ngành

Lọc theo target_province của học sinh → danh sách trường ứng viên cuối cùng


## 8.2 Yêu cầu phi chức năng


## 8.3 Bảo mật

JWT token xác thực tất cả endpoint, hết hạn sau 1 giờ

Học sinh chỉ đọc/ghi dữ liệu của chính mình — kiểm tra student_id từ token

LLM API key lưu ở environment variable, không hardcode trong code

Nội dung hội thoại mã hóa at-rest trong database

Rate limiting: 30 request/phút mỗi session cho endpoint /messages

PDF đề án tuyển sinh chỉ được index, không được phép download trực tiếp


|  |  |
| --- | --- |
| Phiên bản | 1.0 |
| Phạm vi | Phân hệ 1 + Phân hệ 2 + Tích hợp |
| Ngôn ngữ | Tiếng Việt |
| Năm | 2025 |


| Bước | Tên | Đầu vào | Đầu ra |
| --- | --- | --- | --- |
| Bước 1 | Thu thập thông tin | Form nhập liệu | Student profile |
| Bước 2 | Đánh giá RIASEC | Student profile | DCP + gợi ý ngành |
| Bước 3 | Dự đoán tuyển sinh | DCP + profile | Danh sách trường 3 nhóm |


| Web App Next.js / React Học sinh & phụ huynh | Admin Dashboard Next.js Quản trị viên | Mobile App (tuỳ chọn) React Native Truy cập di động |
| --- | --- | --- |


| JWT Authentication Xác thực token | Rate Limiting Giới hạn request | Request Routing Điều hướng service |
| --- | --- | --- |


| Profile Service Bước 1 Lưu student profile | RIASEC Service Bước 2 Hội thoại + DCP | Admission Service Bước 3 ML + phân nhóm | RAG Service Dùng chung Thông tin tuyển sinh |
| --- | --- | --- | --- |


| PostgreSQL Student profiles DCP · Sessions | Vector DB FAISS / Chroma Embedding đề án | ML Model Store XGBoost weights Phiên bản model | File Storage (S3) PDF đề án Nguồn thô |
| --- | --- | --- | --- |


| Dịch vụ | Mục đích | Cách tích hợp |
| --- | --- | --- |
| LLM API (GPT-4o) | Hội thoại RIASEC, chấm điểm, RAG generation | REST API · Bearer key |
| O*NET (Bộ LĐ Mỹ) | 60 câu hỏi RIASEC chuẩn hóa — public domain | Nạp tĩnh vào system prompt |
| Bộ GD&ĐT | Điểm chuẩn lịch sử, phổ điểm THPT | Import định kỳ hàng năm |
| Đề án tuyển sinh PDF | Học phí, học bổng, chỉ tiêu, phương thức xét tuyển | PDF → chunk → embed → Vector DB |


| Tầng | Công nghệ | Lý do chọn |
| --- | --- | --- |
| Frontend | Next.js 14, React, TailwindCSS | SSR, routing tích hợp, hệ sinh thái React |
| Backend | FastAPI (Python 3.11) | Async native, type hints, tự sinh API docs |
| LLM Orchestration | LangChain | Quản lý conversation history, chain |
| ML | XGBoost, scikit-learn | Hiệu năng cao với tabular data, interpretable |
| Database chính | PostgreSQL 16 | ACID, JSONB support, mature |
| Vector DB | FAISS / Chroma | Similarity search nhanh cho RAG |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| student_id | UUID | PK | Khóa chính định danh học sinh |
| full_name | VARCHAR(100) | NOT NULL | Họ và tên đầy đủ |
| email | VARCHAR(200) | UNIQUE · NOT NULL | Email đăng nhập |
| password_hash | VARCHAR(255) | NOT NULL | Mật khẩu đã hash (bcrypt) |
| dob | DATE | NULLABLE | Ngày sinh |
| province | VARCHAR(100) | NOT NULL | Tỉnh/thành phố hiện tại |
| area_code | VARCHAR(5) | NOT NULL | Mã khu vực ưu tiên (KV1/KV2/KV3) |
| priority_group | VARCHAR(10) | NULLABLE | Đối tượng ưu tiên (01–07) |
| target_province | VARCHAR(100) | NULLABLE | Khu vực mong muốn học |
| created_at | TIMESTAMP | NOT NULL | Thời điểm đăng ký |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| record_id | UUID | PK | Khóa chính |
| student_id | UUID | FK · NOT NULL | Liên kết bảng students |
| grade_10_avg | FLOAT | NULLABLE | Điểm TB lớp 10 |
| grade_11_avg | FLOAT | NULLABLE | Điểm TB lớp 11 |
| grade_12_avg | FLOAT | NULLABLE | Điểm TB lớp 12 |
| exam_scores | JSONB | NOT NULL | Điểm thi theo môn: {toan, van, anh, ly, hoa, sinh...} |
| exam_type | VARCHAR(20) | NOT NULL | thpt | dgnl | dgtd |
| exam_year | INTEGER | NOT NULL | Năm thi |
| updated_at | TIMESTAMP | NOT NULL | Lần cập nhật gần nhất |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| session_id | UUID | PK | Khóa chính phiên |
| student_id | UUID | FK · NOT NULL | Liên kết học sinh |
| status | VARCHAR(20) | NOT NULL | in_progress | completed | abandoned |
| question_count | INTEGER | DEFAULT 0 | Số câu đã hỏi |
| current_scores | JSONB | DEFAULT '{}' | Điểm tạm 6 nhóm R/I/A/S/E/C |
| confidence | FLOAT | DEFAULT 0 | Độ tin cậy hiện tại (0.0–1.0) |
| groups_asked | JSONB | DEFAULT '{}' | Số câu đã hỏi mỗi nhóm |
| started_at | TIMESTAMP | NOT NULL | Thời điểm bắt đầu |
| completed_at | TIMESTAMP | NULLABLE | Thời điểm kết thúc |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| message_id | UUID | PK | Khóa chính |
| session_id | UUID | FK · NOT NULL | Liên kết phiên |
| role | VARCHAR(10) | NOT NULL | assistant | user |
| content | TEXT | NOT NULL | Nội dung tin nhắn |
| riasec_target | VARCHAR(3) | NULLABLE | Nhóm nhắm tới (chỉ role=assistant) |
| sequence_no | INTEGER | NOT NULL | Thứ tự trong phiên (1, 2, 3...) |
| created_at | TIMESTAMP | NOT NULL | Thời điểm gửi |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| dcp_id | UUID | PK | Khóa chính |
| student_id | UUID | FK · NOT NULL | Liên kết học sinh |
| session_id | UUID | FK · UNIQUE | Phiên tạo ra DCP này |
| score_R / I / A / S / E / C | FLOAT x6 | NOT NULL | Điểm từng nhóm RIASEC (0–100) |
| riasec_code | VARCHAR(3) | NOT NULL | Mã Holland nổi trội, ví dụ: RI, RIA |
| top_groups | VARCHAR[] | NOT NULL | Mảng nhóm nổi trội: ['R','I'] |
| confidence | FLOAT | NOT NULL | Độ tin cậy kết quả (0.0–1.0) |
| reasoning | TEXT | NULLABLE | Lý giải AI dựa trên bằng chứng hội thoại |
| suggested_majors | JSONB | NOT NULL | Danh sách nhóm ngành gợi ý + mô tả |
| created_at | TIMESTAMP | NOT NULL | Thời điểm tạo DCP |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| record_id | UUID | PK | Khóa chính |
| university_code | VARCHAR(20) | NOT NULL | Mã trường (theo Bộ GD&ĐT) |
| major_code | VARCHAR(20) | NOT NULL | Mã ngành |
| subject_combo | VARCHAR(5) | NOT NULL | Tổ hợp môn (A00, A01, D01...) |
| year | INTEGER | NOT NULL | Năm tuyển sinh |
| cutoff_score | FLOAT | NOT NULL | Điểm chuẩn năm đó |
| quota | INTEGER | NOT NULL | Chỉ tiêu năm đó |
| applicants | INTEGER | NULLABLE | Số thí sinh đăng ký |
| national_avg_score | FLOAT | NULLABLE | Phổ điểm TB toàn quốc tổ hợp này |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| prediction_id | UUID | PK | Khóa chính |
| university_code | VARCHAR(20) | NOT NULL | Mã trường |
| major_code | VARCHAR(20) | NOT NULL | Mã ngành |
| subject_combo | VARCHAR(5) | NOT NULL | Tổ hợp môn |
| target_year | INTEGER | NOT NULL | Năm dự đoán |
| predicted_score | FLOAT | NOT NULL | Điểm chuẩn dự đoán |
| confidence_interval | FLOAT | NOT NULL | Khoảng tin cậy ± |
| model_version | VARCHAR(20) | NOT NULL | Phiên bản model XGBoost dùng |
| created_at | TIMESTAMP | NOT NULL | Thời điểm chạy dự đoán |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| university_code | VARCHAR(20) | PK | Mã trường theo Bộ GD&ĐT |
| name | VARCHAR(200) | NOT NULL | Tên đầy đủ |
| short_name | VARCHAR(50) | NOT NULL | Tên viết tắt |
| province | VARCHAR(100) | NOT NULL | Tỉnh/thành phố |
| type | VARCHAR(20) | NOT NULL | public | private | foreign |
| tier | VARCHAR(20) | NOT NULL | top | mid | local |
| website | VARCHAR(200) | NULLABLE | Website chính thức |
| updated_at | TIMESTAMP | NOT NULL | Lần cập nhật gần nhất |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| major_code | VARCHAR(20) | PK | Mã ngành theo Bộ GD&ĐT |
| name | VARCHAR(200) | NOT NULL | Tên ngành |
| major_group | VARCHAR(100) | NOT NULL | Nhóm ngành (CNTT, Kinh tế, Y dược...) |
| riasec_mapping | VARCHAR[] | NOT NULL | Nhóm RIASEC phù hợp: ['R','I'] |
| description | TEXT | NULLABLE | Mô tả ngành |
| career_prospects | TEXT | NULLABLE | Cơ hội nghề nghiệp |


| Cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| recommendation_id | UUID | PK | Khóa chính |
| student_id | UUID | FK · NOT NULL | Liên kết học sinh |
| dcp_id | UUID | FK · NOT NULL | DCP được dùng để tạo tư vấn |
| university_code | VARCHAR(20) | FK · NOT NULL | Trường được tư vấn |
| major_code | VARCHAR(20) | FK · NOT NULL | Ngành được tư vấn |
| subject_combo | VARCHAR(5) | NOT NULL | Tổ hợp môn xét tuyển |
| predicted_score | FLOAT | NOT NULL | Điểm chuẩn dự đoán |
| student_score | FLOAT | NOT NULL | Điểm học sinh (có tính ưu tiên) |
| group | VARCHAR(20) | NOT NULL | an_toan | can_bang | thu_thach |
| created_at | TIMESTAMP | NOT NULL | Thời điểm tạo tư vấn |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | POST  /auth/register |
| Mô tả | Tạo tài khoản học sinh mới. |
| Request body | { full_name, email, password, province, area_code } |
| Response 200 | { student_id: uuid, token: string } |
| Lỗi | 400 — Email đã tồn tại hoặc dữ liệu không hợp lệ |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | POST  /auth/login |
| Mô tả | Xác thực và trả về JWT token. |
| Request body | { email, password } |
| Response 200 | { token: string, student_id: uuid, expires_in: 3600 } |
| Lỗi | 401 — Email hoặc mật khẩu sai |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | POST  /riasec/sessions |
| Mô tả | Tạo phiên RIASEC mới, trả về câu hỏi đầu tiên ngay lập tức. |
| Request body | { student_id: uuid } |
| Response 200 | { session_id, first_question: string, question_no: 1 } |
| Lỗi | 409 — Phiên in_progress đã tồn tại · 404 — Học sinh không tồn tại |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | POST  /riasec/sessions/{session_id}/messages |
| Mô tả | Nhận câu trả lời, cập nhật state, kiểm tra điều kiện dừng, trả về câu hỏi tiếp hoặc thông báo hoàn thành. |
| Request body | { answer: string  // tối đa 2000 ký tự } |
| Response 200 | // Nếu tiếp tục: { status:'in_progress', next_question, question_no, confidence } // Nếu kết thúc: { status:'completed', dcp_id: uuid } |
| Lỗi | 400 — answer rỗng hoặc quá dài · 409 — Phiên đã completed |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | GET  /riasec/sessions/{session_id} |
| Mô tả | Lấy trạng thái phiên. Frontend polling sau khi nhận status=completed để biết dcp_id. |
| Response 200 | { session_id, status, question_count, confidence, dcp_id | null } |
| Lỗi | 404 — Session không tồn tại |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | GET  /riasec/profiles/{dcp_id} |
| Mô tả | Lấy hồ sơ năng lực số hoàn chỉnh. Endpoint này cũng được Phân hệ 2 gọi nội bộ. |
| Response 200 | { dcp_id, student_id, riasec_code, top_groups,   scores:{ R,I,A,S,E,C },   confidence, reasoning,   suggested_majors:[{ group, majors[], description }],   created_at } |
| Lỗi | 403 — Không có quyền · 404 — DCP không tồn tại |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | PATCH  /riasec/sessions/{session_id}/abandon |
| Mô tả | Đánh dấu phiên abandoned khi học sinh thoát giữa chừng. |
| Response 200 | { session_id, status:'abandoned' } |
| Lỗi | 409 — Phiên đã completed |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | POST  /admission/recommend |
| Mô tả | Tạo danh sách trường tư vấn dựa trên DCP và hồ sơ học sinh. Kết quả được cache 24h. |
| Request body | { student_id: uuid, dcp_id: uuid, target_year: number } |
| Response 200 | { recommendation_id,   an_toan: [{ university, major, predicted_score, student_score, info }],   can_bang: [...],   thu_thach: [...] } |
| Lỗi | 400 — DCP chưa completed · 404 — Student/DCP không tồn tại |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | GET  /admission/predict |
| Mô tả | Tra cứu điểm chuẩn dự đoán cho một cặp ngành-trường cụ thể. |
| Request body | Query params: university_code, major_code, subject_combo, year |
| Response 200 | { predicted_score: float, confidence_interval: float, model_version } |
| Lỗi | 404 — Không đủ dữ liệu lịch sử để dự đoán |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | GET  /admission/history |
| Mô tả | Lấy điểm chuẩn lịch sử nhiều năm của một ngành tại một trường. |
| Request body | Query params: university_code, major_code, subject_combo |
| Response 200 | { history: [{ year, cutoff_score, quota, applicants }] } |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | GET  /admission/recommendations/{recommendation_id} |
| Mô tả | Lấy lại kết quả tư vấn đã lưu. Dùng khi học sinh xem lại. |
| Response 200 | { recommendation_id, created_at, an_toan:[], can_bang:[], thu_thach:[] } |
| Lỗi | 403 — Không có quyền · 404 — Không tồn tại |


| Thuộc tính | Chi tiết |
| --- | --- |
| Endpoint | POST  /rag/query |
| Mô tả | Trả lời câu hỏi về học phí, học bổng, chỉ tiêu, phương thức xét tuyển từ đề án PDF. |
| Request body | { question: string, university_code?: string, major_code?: string } |
| Response 200 | { answer: string, sources: [{ chunk_id, university, page, excerpt }] } |
| Lỗi | 400 — question rỗng · 503 — Vector DB không khả dụng |


| Feature | Kiểu | Ý nghĩa |
| --- | --- | --- |
| cutoff_score_prev | Float | Điểm chuẩn năm trước — feature quan trọng nhất, anchor baseline |
| delta_national_avg | Float | Thay đổi phổ điểm TB toàn quốc so với năm trước |
| ratio_quota_change | Float | Tỷ lệ thay đổi chỉ tiêu so với năm trước |
| avg_competition_ratio_3y | Float | Tỷ lệ chọi trung bình 3 năm (đăng ký / chỉ tiêu) |
| university_tier | Categorical | top | mid | local — được one-hot encode |
| major_group | Categorical | Nhóm ngành (CNTT, Kinh tế, Y dược...) — one-hot encode |
| trend_score | Float [0–1] | Chỉ số xu hướng ngành (tỷ lệ việc làm, mức lương) |
| subject_combo | Categorical | A00, A01, D01... — one-hot encode |


| Mô hình | Lý do | Vai trò | Mục tiêu MAE |
| --- | --- | --- | --- |
| XGBoost | Tabular data, feature importance, xử lý missing | Mô hình chính | < 0.5 điểm |
| Ridge Regression | Đơn giản, dễ giải thích, ít overfit | Baseline | < 0.8 điểm |
| Neural Network | Cần data lớn, khó giải thích | Không dùng | — |


| Điểm gọi | Model | Khi nào gọi | Ghi chú |
| --- | --- | --- | --- |
| PH1 — Hội thoại | gpt-4o-mini | Realtime, mỗi câu trả lời | Ưu tiên tốc độ < 2s response |
| PH1 — Chấm điểm | gpt-4o | Async sau khi dừng hội thoại | Ưu tiên độ chính xác, không giới hạn thời gian |
| RAG — Generation | gpt-4o | Theo request hỏi đáp | Context = top-K chunk + câu hỏi |


| Điều kiện | Ngưỡng | Kết quả |
| --- | --- | --- |
| Confidence đủ cao | Top 2 nhóm cách nhóm 3 > 15% VÀ ổn định qua 3 câu liên tiếp | Dừng sớm — tiết kiệm thời gian học sinh |
| Giới hạn cứng | Tổng câu hỏi đạt 25 | Dừng bắt buộc dù chưa đủ confidence |


| Yêu cầu | Chỉ số mục tiêu | Ghi chú |
| --- | --- | --- |
| Response time — hội thoại | < 2 giây mỗi câu hỏi | Dùng gpt-4o-mini, streaming response |
| Response time — tư vấn tuyển sinh | < 5 giây | Cache kết quả prediction 24h |
| Độ chính xác ML | MAE < 0.5 điểm | Đánh giá trên tập test 2023 |
| RAG Faithfulness | > 0.85 (RAGAS metric) | Không hallucinate thông tin học phí |
| RIASEC Consistency | > 80% trên cùng hồ sơ | Chạy cùng profile 5 lần, top 2 phải ổn định |
| Usability (SUS) | > 70 / 100 | Pilot với 20–30 học sinh thực tế |

