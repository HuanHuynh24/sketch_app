import json
import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Fallback cố định cho ngày hội khi Groq bị lỗi mạng
FIXED_FIRST_SCENARIO = (
    "Chào em! Anh/chị là tư vấn viên hướng nghiệp. "
    "Hôm nay mình sẽ trò chuyện để tìm hiểu sở thích và xu hướng nghề nghiệp của em nhé!\n\n"
    "Trường em sắp tổ chức một ngày hội lớn. Ban tổ chức cần người. "
    "Nếu em được tự chọn, em muốn phụ trách phần nào nhất và tại sao?"
)

RIASEC_KEYWORDS = {
    "R": ["sửa chữa", "máy móc", "thể thao", "tập thể dục", "tay chân", "ngoài trời",
          "lắp ráp", "xây dựng", "kỹ thuật", "thiên nhiên", "sơn", "sửa", "lắp",
          "trồng", "robot", "xe", "chạy bộ", "bơi", "bóng đá", "vận động", "câu cá"],
    "I": ["nghiên cứu", "phân tích", "khoa học", "thí nghiệm", "toán", "logic",
          "tìm hiểu", "đọc sách", "dữ liệu", "quan sát", "giải đố", "tra cứu",
          "kết luận", "thiên văn", "lập trình", "sudoku", "chi tiết", "tò mò"],
    "A": ["sáng tạo", "vẽ", "thiết kế", "âm nhạc", "hát", "nhảy", "kịch", "phim",
          "ảnh", "viết", "nghệ thuật", "thời trang", "trang trí", "guitar", "piano",
          "origami", "thơ", "truyện", "ngoại ngữ", "sáng tác"],
    "S": ["giúp đỡ", "dạy", "hướng dẫn", "bạn bè", "nhóm", "cộng đồng",
          "tình nguyện", "chia sẻ", "lắng nghe", "chăm sóc", "hòa nhập",
          "động viên", "quan tâm", "mọi người", "thân thiện", "kết bạn"],
    "E": ["lãnh đạo", "tổ chức", "kinh doanh", "bán", "thuyết phục", "quản lý",
          "tiền", "mạo hiểm", "quyền", "quyết định", "điều phối", "gây quỹ",
          "khởi nghiệp", "lớp trưởng", "ứng cử", "nổi bật"],
    "C": ["ngăn nắp", "gọn gàng", "lập kế hoạch", "danh sách", "kiểm tra",
          "chính xác", "hệ thống", "quy trình", "sổ sách", "nhập liệu",
          "phân loại", "to-do", "biên bản", "excel", "ghi chép"],
}

RIASEC_QUESTIONS_REF = """
BỘ 60 CÂU HỎI RIASEC LÀM NGUỒN CẢM HỨNG:
[R] 1. Thích lắp ráp máy móc. 2. Làm việc với đồ gỗ. 3. Tò mò về thế giới xung quanh. 4. Người độc lập. 5. Thích sửa chữa đồ vật. 6. Thích làm việc dùng tay chân. 7. Thích tập thể dục. 8. Thích dành dụm tiền. 9. Thích làm việc đến khi hoàn thành. 10. Thích làm việc một mình.
[I] 11. Hay để ý chi tiết. 12. Tò mò về mọi thứ. 13. Tính toán bài toán phức tạp. 14. Thích giải bài tập toán. 15. Thích sử dụng máy tính. 16. Rất thích đọc sách. 17. Thích sưu tập. 18. Thích trò chơi ô chữ. 19. Thích học các môn khoa học. 20. Thích thách thức.
[A] 21. Rất sáng tạo. 22. Thích vẽ/tô màu. 23. Chơi nhạc cụ. 24. Thiết kế thời trang. 25. Đọc truyện/thơ ca. 26. Mỹ thuật/thủ công. 27. Xem nhiều phim. 28. Thích chụp ảnh. 29. Thích học ngoại ngữ. 30. Thích hát/đóng kịch/nhảy.
[S] 31. Rất thân thiện. 32. Thích dạy/hướng dẫn người khác. 33. Nói chuyện trước đám đông. 34. Làm việc tốt trong nhóm. 35. Điều hành thảo luận. 36. Thích giúp đỡ người khác. 37. Thể thao đồng đội. 38. Tham gia các buổi tiệc. 39. Kết bạn mới. 40. Tham gia hoạt động cộng đồng.
[E] 41. Thích học về tài chính. 42. Thích bán hàng. 43. Nghĩ mình khá nổi bật. 44. Thích lãnh đạo. 45. Giữ vai trò quan trọng trong nhóm. 46. Thích có quyền. 47. Muốn sở hữu doanh nghiệp. 48. Thích tiết kiệm tiền. 49. Làm việc đến khi hoàn tất. 50. Thích mạo hiểm.
[C] 51. Thích gọn gàng. 52. Giữ không gian ngăn nắp. 53. Thích sưu tầm thông tin. 54. Lập danh sách công việc. 55. Sử dụng máy tính. 56. Cân nhắc chi phí khi mua. 57. Thích đánh máy hơn viết tay. 58. Làm công việc thư ký. 59. Kiểm tra lại việc đã làm. 60. Viết thư từ cho người khác.
"""

MAJORS_MAPPING = """
I. Nhóm ngành Công nghệ thông tin
1. Khoa học máy tính
2. Công nghệ phần mềm
3. Mạng máy tính và truyền thông dữ liệu
4. An ninh mạng
5. Hệ thống thông tin quản lý
6. Cơ sở dữ liệu
7. Công nghệ web
8. Trí tuệ nhân tạo
9. Internet vạn vật (IoT)
10. Thực tế Ảo (VR) và Thực tế Tăng cường (AR)
II. Nhóm ngành Kinh doanh
1. Ngành quản trị kinh doanh.
2. Ngành quản trị dịch vụ du lịch và lữ hành
3. Ngành quản trị khách sạn
4. Ngành Marketing
5. Ngành nghề bất động sản
6. Ngành kinh doanh quốc tế
7. Ngành kế toán
8. Ngành kiểm toán
9. Ngành quản trị nhân lực
10. Ngành hệ thống thông tin quản lý
11. Ngành quản trị văn phòng
12. Ngành Kinh tế
III. Nhóm ngành Kiến trúc và xây dựng
1. Ngành quy hoạch đô thị
2. Ngành kiến trúc công trình
3. Ngành kỹ thuật công trình
4. Ngành xây dựng cầu đường
5. Ngành vật liệu và cấu kiện xây dựng
6. Ngành xây dựng cảng – công trình biển
7. Ngành thủy lợi – thủy điện và cấp thoát nước
8. Ngành công trình thủy lợi
9. Kỹ thuật xây dựng công trình giao thông
10. Ngành Thiết kế nội thất
11. Ngành Thiết kế công nghiệp 
IV. Nhóm ngành Luật – Nhân văn
1. Ngành Luật Kinh tế
2. Ngành Luật Quốc tế
3. Ngành Luật 
4. Ngành Hàn Quốc học
5. Ngành Nhật Bản học 
6. Ngành Hán Nôm
7. Ngành Triết học
8. Ngành Trung Quốc học 
9. Ngành Văn hóa học
10. Ngành Quản lý văn hóa
11. Ngành Lịch sử học 
12. Các ngành ngôn ngữ 
13. Ngành Nghệ thuật biểu diễn
14. Ngành Tôn giáo 
V. Nhóm ngành báo chí
1. Các ngành Báo chí 
2. Ngành Truyền thông đa phương tiện
3. Ngành công nghệ truyền thông
4. Ngành quan hệ công chúng
VI. Nhóm ngành Khoa học cơ bản 
1. Ngành công nghệ sinh học
2. Ngành sinh học
3. Ngành kỹ thuật sinh học
4. Ngành sinh học ứng dụng
5. Ngành thiên văn học
6. Ngành vật lý học
7. Ngành khoa học đất
8. Ngành toán học
9. Ngành toán ứng dụng
10. Ngành thống kê
VII. Nhóm ngành Sư phạm
1. Giáo dục Tiểu học
2. Giáo dục Mầm non
3. Giáo dục Chính trị
4. Giáo dục Thể chất
5. Sư phạm Toán học
6. Sư phạm Tin học
7. Sư phạm Vật lý
8. Sư phạm Sinh học
9. Sư phạm Hoá học
10. Sư phạm Ngữ văn
11. Sư phạm Lịch sử
12. Sư phạm Địa lý
13. Sư phạm Tiếng Anh
14. Ngành giáo dục quốc phòng – an ninh
15. Ngành giáo dục đặc biệt
16. Ngành quản lý giáo dục
17. Ngành Sư phạm Âm nhạc…
VIII. Nhóm ngành nông – lâm – ngư nghiệp
1. Ngành nông nghiệp (các ngành nông nghiệp – thú y)
2. Ngành khuyến nông
3. Ngành chăn nuôi
4. Ngành nông học
5. Ngành khoa học cây trồng
6. Ngành bảo vệ thực vật học gì và làm gì?
7. Ngành công nghệ rau hoa quả – cảnh quan
8. Ngành kinh doanh nông nghiệp
9. Ngành kinh tế nông nghiệp
10. Ngành phát triển nông thôn
IX. Nhóm ngành sản xuất và chế biến
1. Ngành công nghệ thực phẩm
2. Ngành công nghệ chế biến sau thu hoạch
3. Công nghệ chế biến thủy sản
4. Ngành kỹ thuật dệt
5. Công nghệ sợi dệt
6. Ngành công nghệ may học gì và làm gì?
7. Công nghệ da giầy
8. Công nghệ chế biến lâm sản
X. Nhóm ngành sức khỏe
1. Y đa khoa
2. Y học cổ truyền
3. Điều dưỡng
4. Răng hàm mặt
5. Dược 
6. Y tế công cộng
7. Y học dự phòng
8. Hộ sinh
XI. Nhóm ngành Kỹ thuật 
1. Công nghệ kỹ thuật nhiệt
2. Công nghệ kỹ thuật hóa học 
3. Công nghệ kỹ thuật
4. Công nghệ kỹ thuật cơ – điện tử 
5. Công nghệ kỹ thuật năng lượng
6. Công nghệ kỹ thuật điện tử – viễn thông
7. Công nghệ kỹ thuật điều khiển và tự động hóa
8. Kỹ thuật dầu khí 
9. Kỹ thuật nhiệt
10. Công nghệ kỹ thuật ô tô
11. Kỹ thuật Robot
"""


SYSTEM_INSTRUCTION_AGENT = f"""Bạn là chuyên gia tư vấn hướng nghiệp thân thiện đang trò chuyện để đánh giá tính cách và sở thích.

[NGUYÊN TẮC]
1. KHÔNG tiết lộ bạn đang dùng mô hình RIASEC. KHÔNG liệt kê câu hỏi trắc nghiệm trực tiếp.
2. Tình huống TỰ DO: tạo ra một tình huống đời thực dựa trên [BỘ 60 CÂU HỎI RIASEC]. KHÔNG BẮT BUỘC mang bối cảnh học sinh THPT, có thể linh hoạt mọi ngữ cảnh. Tình huống có thể mở để đánh giá 1-3 nhóm RIASEC cùng lúc, giúp người dùng bộc lộ rõ tính cách.
3. TUYỆT ĐỐI KHÔNG lặp lại các tình huống đã từng hỏi trong lịch sử hội thoại. Hãy đọc kỹ lịch sử để tạo tình huống hoàn toàn mới.
4. BẮT ĐẦU bằng phản hồi ngắn 1 câu (khen/nhận xét) về câu trả lời trước → rồi đưa ra tình huống mới 2-4 câu, kết thúc bằng câu hỏi mở.
5. Chỉ trả về lời nói của bạn, không nhãn, không metadata.

[Nguồn Cảm Hứng]
{RIASEC_QUESTIONS_REF}
"""

EXTRACT_SIGNAL_PROMPT = """You are a precise data extraction assistant. Your task is to analyze the student's answer and extract RIASEC signals.
R=physical/hands-on | I=analytical/science | A=creative/arts
S=helping/community | E=leadership/business | C=order/records

Rate each group from 0 to 3 based on the user's answer.
Question: {question}
Answer: {answer}

You must return a valid json object with the following schema:
{"signals": {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}, "answer_quality": "clear|vague|off_topic"}"""

# SỬA: Chuyển đổi thành string thường tuyệt đối, loại bỏ tiền tố 'f' và thay thế thủ công bằng .replace()
# Điều này triệt tiêu hoàn toàn lỗi KeyError do dấu ngoặc nhọn lồng nhau khi gọi .format()
SYSTEM_PROMPT_SCORING = """You are an advanced career guidance analyzer. Analyze the entire conversation history below, normalize scores to 0-100 for the 6 RIASEC groups, and generate suggestions.
- Based on the conversation history, calculate scores for R, I, A, S, E, C.
- Determine top 2 or 3 groups as `riasec_code`.
- Create a `reasoning` in Vietnamese explaining why you chose những nhóm này và bộc lộ tính cách như thế nào thông qua lịch sử hội thoại.
- Suggest majors based on this list of 11 groups:
{MAJORS_MAPPING}

[CONVERSATION HISTORY]
{conversation_history}

You must output a valid json object with the following exact keys and format:
{
  "scores": {
    "R": 0.0,
    "I": 0.0,
    "A": 0.0,
    "S": 0.0,
    "E": 0.0,
    "C": 0.0
  },
  "riasec_code": "XYZ",
  "top_groups": ["X", "Y"],
  "confidence": 0.0,
  "reasoning": "Lý giải chi tiết bằng tiếng Việt...",
  "suggested_majors": [
    {
      "group": "Tên nhóm ngành gợi ý...",
      "majors": ["Ngành 1", "Ngành 2"],
      "fit_reason": "Lý do phù hợp bằng tiếng Việt..."
    }
  ]
}"""



def _keyword_extract_signal(answer: str) -> dict:
    answer_lower = answer.lower()
    signals = {}
    for group, keywords in RIASEC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in answer_lower)
        signals[group] = min(score, 3)
    return signals


async def call_groq_api(messages: list, response_format: dict = None) -> str:
    """Helper gọi Groq API siêu tốc với cơ chế tự động thử lại (Fallback) nếu model gặp lỗi."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    models_to_try = [
        settings.GROQ_MODEL,               # llama-3.3-70b-versatile
        "llama-3.3-70b-specdec",
        "mixtral-8x7b-32768",
        "llama3-8b-8192"
    ]

    for model in models_to_try:
        if not model:
            continue
            
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3, # Giảm nhiệt độ xuống thấp để định dạng JSON đầu ra cực kỳ chính xác
            "max_tokens": 1500
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    result_json = resp.json()
                    content = result_json["choices"][0]["message"]["content"].strip()
                    logger.info(f"[GROQ SERVICE] Success calling model {model}")
                    return content
                else:
                    logger.warning(f"[GROQ SERVICE] Model {model} failed (status {resp.status_code}): {resp.text}")
        except Exception as e:
            logger.error(f"[GROQ SERVICE] Exception when calling {model}: {e}")
            
    logger.error("[GROQ SERVICE] All fallback models failed to respond!")
    return ""


async def generate_greeting() -> str:
    """Tạo tình huống đầu tiên bằng Groq Llama 3."""
    if settings.GROQ_API_KEY:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION_AGENT},
            {"role": "user", "content": "Tạo một tình huống mở đầu để bắt đầu trò chuyện hướng nghiệp với học sinh. Tình huống này nên mở và bao quát, không quá thiên về một nhóm cụ thể."}
        ]
        text = await call_groq_api(messages)
        if text:
            return text
    return FIXED_FIRST_SCENARIO


async def generate_question(
    question_no: int,
    target_groups: list,
    saturated_groups: list,
    history: list,
    groups_asked: dict = None,
) -> str:
    """Yêu cầu Groq tạo tình huống mới hoàn toàn tự do."""
    primary_target = target_groups[0] if target_groups else "R"

    if settings.GROQ_API_KEY:
        user_instruction = (
            f"Đây là lượt hỏi số {question_no}.\n"
            f"Mục tiêu chính: Đặt một tình huống TỰ DO dựa trên BỘ 60 CÂU HỎI RIASEC để khám phá sự phù hợp với nhóm {primary_target}.\n"
            f"Các nhóm đã đủ thông tin (hạn chế xoáy vào): {', '.join(saturated_groups) if saturated_groups else 'Chưa có'}.\n"
            "Yêu cầu: Tình huống có thể kết hợp 1-3 nhóm RIASEC để người dùng lựa chọn. Đọc kỹ lịch sử hội thoại trên, KHÔNG lặp lại chủ đề hay bối cảnh đã dùng."
        )
        
        messages = [{"role": "system", "content": SYSTEM_INSTRUCTION_AGENT}]
        for msg in history:
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({"role": role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_instruction})
        
        text = await call_groq_api(messages)
        if text:
            return text

    return f"Câu trả lời của em giúp anh/chị hiểu thêm nhiều điều! Nếu em tham gia một hoạt động liên quan đến {primary_target}, em sẽ thích làm công việc cụ thể nào nhất?"


async def extract_signal(question: str, answer: str) -> dict:
    """Gọi Groq trích xuất tín hiệu dưới dạng JSON."""
    if not settings.GROQ_API_KEY:
        return {"signals": _keyword_extract_signal(answer), "answer_quality": "clear"}
        
    # SỬA: Thay thế an toàn bằng .replace thay vì .format() để triệt tiêu hoàn toàn KeyError do dấu ngoặc nhọn JSON
    prompt = (
        EXTRACT_SIGNAL_PROMPT
        .replace("{question}", question)
        .replace("{answer}", answer)
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    response_text = await call_groq_api(messages, response_format={"type": "json_object"})
    if response_text:
        try:
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed parsing Groq signal JSON: {e}. Raw response: {response_text}")
            
    return {"signals": _keyword_extract_signal(answer), "answer_quality": "clear"}



async def generate_final_scoring(history_text: str) -> dict:
    """Gọi Groq tính toán điểm chi tiết cuối cùng dạng JSON."""
    if not settings.GROQ_API_KEY:
        return None
        
    # SỬA: Thay thế an toàn bằng .replace thay vì .format để triệt tiêu hoàn toàn KeyError do dấu ngoặc nhọn lồng nhau của JSON schema
    prompt = (
        SYSTEM_PROMPT_SCORING
        .replace("{MAJORS_MAPPING}", MAJORS_MAPPING)
        .replace("{conversation_history}", history_text)
    )
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    response_text = await call_groq_api(messages, response_format={"type": "json_object"})
    if response_text:
        try:
            parsed_json = json.loads(response_text)
            logger.info(f"[GROQ SERVICE] Successfully generated final scoring report: {parsed_json.keys()}")
            return parsed_json
        except Exception as e:
            logger.error(f"Failed parsing Groq final scores JSON: {e}. Raw response: {response_text}")
            
    return None
