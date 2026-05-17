class PromptEngine:
    def build_query_generation_prompt(
        self,
        student_profile: dict,
        riasec_result: dict,
    ) -> str:
        return f"""
Bạn là chuyên gia tư vấn tuyển sinh và chuyên gia xây dựng câu truy vấn tìm kiếm (Query Builder).

Thông tin Học thuật và Mong muốn của học sinh (Từ Profile):
{student_profile}

Kết quả phân tích hướng nghiệp RIASEC:
{riasec_result}

Nhiệm vụ:
Tổng hợp tất cả dữ liệu trên và tạo ra một câu truy vấn tìm kiếm (Search Query) tiếng Anh cực kỳ tối ưu để đưa vào các công cụ tìm kiếm như Tavily Search hoặc Vector Database. Đồng thời trích xuất các metadata quan trọng.

Quy tắc tạo Search Query:
1. Ngôn ngữ truy vấn (Quan trọng): 
   - Nếu `target_country` hoặc `target_province` là "Vietnam" hoặc "Việt Nam", PHẢI TẠO QUERY BẰNG TIẾNG VIỆT (Ví dụ: "Tuyển sinh đại học ngành trí tuệ nhân tạo khối A00 học phí dưới 30 triệu").
   - Nếu là quốc gia khác, tạo query bằng Tiếng Anh.
2. Tập trung vào: tên ngành học (majors), khối thi (nếu ở VN: Toán Lý Hoá, Toán Văn...), bằng cấp (undergraduate/bachelor), quốc gia mục tiêu, điểm IELTS, và budget.
3. Độ dài query: ngắn gọn, nhiều từ khóa chuẩn SEO/Search.
4. Loại bỏ các từ thừa, đại từ nhân xưng.

Quy tắc extract Metadata:
1. `target_countries`: Các quốc gia học sinh muốn đến (ví dụ: ["Australia", "Singapore"]). Nếu học sinh chọn Việt Nam thì để ["Vietnam"].
2. `target_majors`: Các ngành học được gợi ý cao nhất từ RIASEC hoặc học sinh tự chọn.
3. `budget_limit_usd`: Quy đổi ngân sách (nếu có) ra USD. Nếu không có thì để null.
4. `min_ielts`: Điểm IELTS hiện tại của học sinh. Null nếu không có.
5. `keywords`: Các từ khóa quan trọng khác (e.g., "scholarship", "financial aid").

Chỉ trả về định dạng JSON hợp lệ:
{{
  "optimized_query": "...",
  "target_countries": ["..."],
  "target_majors": ["..."],
  "budget_limit_usd": 15000,
  "min_ielts": 6.5,
  "keywords": ["..."]
}}
"""
