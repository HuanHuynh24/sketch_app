class PromptEngine:
    def build_anchor_prompt(self) -> str:
        return """
Bạn là chuyên gia tư vấn hướng nghiệp theo mô hình Holland RIASEC.

Tạo đúng 1 câu hỏi tình huống đầu tiên cho học sinh THPT Việt Nam.

Mục tiêu:
- Câu hỏi đầu tiên phải mở đủ cơ hội để học sinh bộc lộ cả 6 nhóm RIASEC.
- R: thực hành, kỹ thuật, thiết bị, thao tác thực tế.
- I: phân tích, nghiên cứu, dữ liệu, logic.
- A: sáng tạo, thiết kế, ý tưởng, nội dung.
- S: hỗ trợ, tư vấn, hướng dẫn, giúp đỡ người khác.
- E: lãnh đạo, thuyết phục, điều phối, kinh doanh.
- C: quy trình, kế hoạch, kiểm tra, chính xác.

Yêu cầu về tình huống:
- Bối cảnh phải giống đời sống học sinh THPT Việt Nam hiện tại: lớp học, CLB, ngày hội hướng nghiệp, dự án truyền thông, hoạt động trải nghiệm, deadline gấp.
- Có một chi tiết cụ thể làm tình huống sống động hơn, ví dụ: sắp đến giờ thuyết trình, nhóm thiếu người, số liệu bị rối, gian hàng chưa thu hút, bạn trong nhóm đang lúng túng.
- Câu hỏi nghe như người tư vấn đang trò chuyện, không giống đề thi.
- Không liệt kê quá dài các vai trò khô cứng.
- Không dùng trắc nghiệm A/B/C.
- Chỉ dùng 1 tình huống chính và 1 câu hỏi chính.
- Không quá 90 từ.
- Không giải thích ngoài JSON.

Return only valid JSON:
{
  "type": "anchor_scenario",
  "content": "...",
  "focus_groups": ["R", "I", "A", "S", "E", "C"],
  "context": "anchor",
  "question_style": "role_choice"
}
"""

    def build_answer_quality_prompt(
        self,
        scenario: str,
        answer_text: str,
    ) -> str:
        return f"""
Bạn là hệ thống kiểm tra chất lượng câu trả lời cho bài đánh giá hướng nghiệp RIASEC.

Tình huống đang hỏi:
{scenario}

Câu trả lời của học sinh:
{answer_text}

Nhiệm vụ:
Xác định câu trả lời có nghiêm túc và đúng trọng tâm tình huống không.

Câu trả lời KHÔNG hợp lệ nếu:
- Quá ngắn, ví dụ: "không biết", "ok", "abc", "haha", "tùy", "sao cũng được".
- Không liên quan đến tình huống.
- Chửi tục, spam, ký tự vô nghĩa.
- Không thể hiện lựa chọn, sở thích, hành vi hoặc lý do.
- Trả lời né tránh khiến hệ thống không thể đánh giá RIASEC.

Câu trả lời hợp lệ nếu:
- Có mô tả người dùng muốn chọn hướng nào.
- Có lý do hoặc hành vi cụ thể.
- Dù ngắn nhưng vẫn liên quan và đánh giá được.

Return only valid JSON:
{{
  "is_valid": true,
  "reason": "...",
  "warning_message": null
}}

Nếu không hợp lệ:
{{
  "is_valid": false,
  "reason": "...",
  "warning_message": "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm. Hãy trả lời nghiêm túc hơn bằng cách nói bạn sẽ chọn hướng nào và vì sao."
}}
"""

    def build_scoring_prompt(
        self,
        scenario: str,
        answer_text: str,
    ) -> str:
        return f"""
Bạn là hệ thống chấm điểm RIASEC cho học sinh THPT Việt Nam.

Tình huống đã hỏi:
{scenario}

Câu trả lời của học sinh:
{answer_text}

Nhiệm vụ:
Chấm điểm từng nhóm RIASEC từ 0 đến 2 dựa trên bằng chứng có trong câu trả lời.

Quy tắc điểm:
- 0: không có tín hiệu.
- 0.5: tín hiệu yếu.
- 1.0: tín hiệu vừa.
- 1.5: tín hiệu rõ.
- 2.0: tín hiệu rất mạnh.

Ý nghĩa nhóm:
- R: thích thực hành, máy móc, kỹ thuật, thiết bị, thao tác thực tế.
- I: thích phân tích, nghiên cứu, dữ liệu, logic, tìm nguyên nhân.
- A: thích sáng tạo, thiết kế, ý tưởng, nội dung, nghệ thuật.
- S: thích giúp đỡ, hướng dẫn, tư vấn, hỗ trợ người khác.
- E: thích lãnh đạo, thuyết phục, kinh doanh, điều phối, tạo ảnh hưởng.
- C: thích quy trình, dữ liệu có cấu trúc, kế hoạch, kiểm tra, chính xác.

Yêu cầu đánh giá:
- Chấm theo hành vi người dùng thể hiện, không suy diễn quá mức.
- Nếu câu trả lời mơ hồ, điểm và confidence phải thấp.
- Không tự thêm thông tin không có trong câu trả lời.
- confidence mỗi nhóm từ 0 đến 1.
- primary_groups là 1-3 nhóm có bằng chứng rõ nhất.
- evidence phải chỉ ra group, quote ngắn từ câu trả lời, strength và confidence.
- Không chấm điểm cao cho nhóm nếu không có evidence rõ.
- reasoning ngắn gọn bằng tiếng Việt.
- detected_traits là các tín hiệu hành vi rút ra trực tiếp từ câu trả lời.
- Không giải thích ngoài JSON.

Return only valid JSON:
{{
  "scores": {{
    "R": 0,
    "I": 0,
    "A": 0,
    "S": 0,
    "E": 0,
    "C": 0
  }},
  "confidence": {{
    "R": 0,
    "I": 0,
    "A": 0,
    "S": 0,
    "E": 0,
    "C": 0
  }},
  "reasoning": "...",
  "detected_traits": ["..."],
  "primary_groups": ["I", "C"],
  "evidence": [
    {{
      "group": "I",
      "quote": "trích dẫn ngắn từ câu trả lời",
      "strength": 1.5,
      "confidence": 0.8
    }}
  ]
}}
"""

    def build_adaptive_prompt(
        self,
        history: list[dict],
        scores: dict,
        confidence: dict,
        focus_groups: list[str],
        suggested_context: str,
        banned_topics: list[str],
        question_number: int,
        question_style: str,
    ) -> str:
        return f"""
Bạn là chuyên gia tư vấn hướng nghiệp theo mô hình Holland RIASEC.

Câu hỏi số: {question_number}
Điểm hiện tại: {scores}
Độ tin cậy hiện tại: {confidence}
Nhóm cần phân biệt rõ hơn: {focus_groups}
Bối cảnh nên dùng: {suggested_context}
Kiểu câu hỏi nên dùng: {question_style}
Chủ đề/cụm từ cần tránh: {banned_topics}
Lịch sử hội thoại gần nhất: {history}

Hãy tạo đúng 1 câu hỏi tình huống tiếp theo.

Yêu cầu bắt buộc:
- Tập trung phân biệt nhóm: {focus_groups}.
- Dùng bối cảnh gần với học sinh THPT Việt Nam.
- Tình huống phải có chi tiết đời thực và một áp lực nhỏ: deadline, thiếu dữ liệu, nhóm chưa thống nhất, sản phẩm lỗi, người tham gia ít, hoặc phải chọn ưu tiên.
- Câu hỏi phải khiến học sinh kể hành động cụ thể, không chỉ trả lời "em thích".
- Không lặp lại câu chữ, bối cảnh hoặc chủ đề trong lịch sử.
- Không dùng lại các chủ đề/cụm từ cần tránh.
- Không dùng trắc nghiệm A/B/C.
- Không hỏi lý thuyết RIASEC.
- Không hỏi quá rộng kiểu "bạn thích làm gì".
- Viết tự nhiên như người tư vấn học đường đang hỏi học sinh.
- Chỉ dùng 1 tình huống chính và 1 câu hỏi chính.
- Không nhồi quá 3 hướng lựa chọn trong một câu.
- Nội dung dưới 90 từ.
- Không giải thích ngoài JSON.

Gợi ý theo question_style:
- role_choice: hỏi học sinh muốn nhận vai trò nào trong một tình huống cụ thể.
- trade_off: cho 2 hướng hành động khác nhau và hỏi em nghiêng về hướng nào hơn.
- priority_ranking: hỏi em sẽ ưu tiên việc gì trước khi thời gian có hạn.
- conflict_scenario: đặt một mâu thuẫn nhẹ trong nhóm/dự án.
- resource_constraint: đặt tình huống thiếu thời gian/người/nguồn lực.
- reflection: hỏi từ trải nghiệm cá nhân gần đây nhưng vẫn gắn với một tình huống cụ thể.
- next_action: hỏi bước đầu tiên em sẽ làm.

Return only valid JSON:
{{
  "type": "adaptive_scenario",
  "content": "...",
  "focus_groups": {focus_groups},
  "context": "{suggested_context}",
  "question_style": "{question_style}"
}}
"""

    def build_final_report_prompt(
        self,
        history: list[dict],
        scores: dict,
        confidence: dict,
        riasec_code: str,
        career_groups: list[str],
        recommended_majors: list[str],
        suitable_roles: list[str],
        digital_competencies: dict,
    ) -> str:
        return f"""
Bạn là chuyên gia hướng nghiệp cho học sinh THPT Việt Nam.

Mã RIASEC: {riasec_code}
Điểm: {scores}
Độ tin cậy: {confidence}
Nhóm ngành hệ thống gợi ý: {career_groups}
Ngành học gợi ý: {recommended_majors}
Vai trò/công việc phù hợp: {suitable_roles}
Năng lực số nên phát triển: {digital_competencies}
Lịch sử trả lời: {history}

Hãy viết báo cáo cá nhân hóa ngắn gọn.

Yêu cầu:
- summary tối đa 5 câu.
- strengths: nêu 3-5 điểm mạnh nổi bật.
- suitable_career_groups: nhóm ngành phù hợp.
- recommended_majors: ngành học cụ thể phù hợp.
- suitable_roles: vai trò/công việc phù hợp.
- learning_suggestions: kỹ năng nên học tiếp.
- career_advice: lời khuyên định hướng.
- Không kết luận tuyệt đối.
- Không nói đây là chẩn đoán.
- Phù hợp học sinh THPT Việt Nam.
- Không giải thích ngoài JSON.

Return only valid JSON:
{{
  "summary": "...",
  "strengths": ["..."],
  "suitable_career_groups": ["..."],
  "recommended_majors": ["..."],
  "suitable_roles": ["..."],
  "learning_suggestions": ["..."],
  "career_advice": ["..."]
}}
"""
