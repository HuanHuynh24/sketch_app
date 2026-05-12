import json
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
genai.configure(api_key=settings.GEMINI_API_KEY)

FIXED_FIRST_SCENARIO = (
    "Chào em! Anh/chị là tư vấn viên hướng nghiệp. "
    "Hôm nay mình sẽ trò chuyện để tìm hiểu sở thích và xu hướng nghề nghiệp của em nhé!\n\n"
    "Trường em sắp tổ chức một ngày hội lớn. Ban tổ chức cần người. "
    "Nếu em được tự chọn, em muốn phụ trách phần nào nhất và tại sao?"
)

# Keyword matching — fallback cho extract_signal
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
BỘ 60 CÂU HỎI RIASEC LÀM NGUỒN CẢM HỨNG (Cơ sở để xây dựng tình huống):
[R] 1. Thích lắp ráp máy móc. 2. Làm việc với đồ gỗ. 3. Tò mò về thế giới xung quanh. 4. Người độc lập. 5. Thích sửa chữa đồ vật. 6. Thích làm việc dùng tay chân. 7. Thích tập thể dục. 8. Thích dành dụm tiền. 9. Thích làm việc đến khi hoàn thành. 10. Thích làm việc một mình.
[I] 11. Hay để ý chi tiết. 12. Tò mò về mọi thứ. 13. Tính toán bài toán phức tạp. 14. Thích giải bài tập toán. 15. Thích sử dụng máy tính. 16. Rất thích đọc sách. 17. Thích sưu tập. 18. Thích trò chơi ô chữ. 19. Thích học các môn khoa học. 20. Thích thách thức.
[A] 21. Rất sáng tạo. 22. Thích vẽ/tô màu. 23. Chơi nhạc cụ. 24. Thiết kế thời trang. 25. Đọc truyện/thơ ca. 26. Mỹ thuật/thủ công. 27. Xem nhiều phim. 28. Thích chụp ảnh. 29. Thích học ngoại ngữ. 30. Thích hát/đóng kịch/nhảy.
[S] 31. Rất thân thiện. 32. Thích dạy/hướng dẫn người khác. 33. Nói chuyện trước đám đông. 34. Làm việc tốt trong nhóm. 35. Điều hành thảo luận. 36. Thích giúp đỡ người khác. 37. Thể thao đồng đội. 38. Tham gia các buổi tiệc. 39. Kết bạn mới. 40. Tham gia hoạt động cộng đồng.
[E] 41. Thích học về tài chính. 42. Thích bán hàng. 43. Nghĩ mình khá nổi bật. 44. Thích lãnh đạo. 45. Giữ vai trò quan trọng trong nhóm. 46. Thích có quyền. 47. Muốn sở hữu doanh nghiệp. 48. Thích tiết kiệm tiền. 49. Làm việc đến khi hoàn tất. 50. Thích mạo hiểm.
[C] 51. Thích gọn gàng. 52. Giữ không gian ngăn nắp. 53. Thích sưu tầm thông tin. 54. Lập danh sách công việc. 55. Sử dụng máy tính. 56. Cân nhắc chi phí khi mua. 57. Thích đánh máy hơn viết tay. 58. Làm công việc thư ký. 59. Kiểm tra lại việc đã làm. 60. Viết thư từ cho người khác.
"""

MAJORS_MAPPING = """
I. Nhóm ngành Công nghệ thông tin
II. Nhóm ngành Kinh doanh
III. Nhóm ngành Kiến trúc và xây dựng
IV. Nhóm ngành Luật – Nhân văn
V. Nhóm ngành báo chí
VI. Nhóm ngành Khoa học cơ bản
VII. Nhóm ngành Sư phạm
VIII. Nhóm ngành nông – lâm – ngư nghiệp
IX. Nhóm ngành sản xuất và chế biến
X. Nhóm ngành sức khỏe
XI. Nhóm ngành Kỹ thuật
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

EXTRACT_SIGNAL_PROMPT = """Phân tích câu trả lời học sinh, trích xuất tín hiệu RIASEC.
R=tay chân,kỹ thuật | I=phân tích,khoa học | A=sáng tạo,nghệ thuật
S=giúp đỡ,cộng đồng | E=lãnh đạo,kinh doanh | C=quy trình,dữ liệu
Chấm mỗi nhóm 0-3. Câu hỏi: {question} | Trả lời: {answer}
JSON: {{"signals":{{"R":0,"I":0,"A":0,"S":0,"E":0,"C":0}},"answer_quality":"clear|vague|off_topic"}}"""

SYSTEM_PROMPT_SCORING = f"""Phân tích TOÀN BỘ hội thoại, chuẩn hoá điểm 0-100 cho 6 nhóm RIASEC.
- Dựa trên lịch sử hội thoại, tính điểm cho R, I, A, S, E, C.
- Xác định top 2 hoặc 3 nhóm (riasec_code).
- Tạo `reasoning` (Lý do chọn nhóm).
- Tạo `description`: Một câu nhận xét ngắn, ví dụ "Bạn là kiểu người thích sáng tạo, với trí tưởng tượng phong phú".
- Gợi ý chuyên ngành dựa vào danh sách 11 nhóm ngành sau:
{MAJORS_MAPPING}

[HỘI THOẠI]
{{conversation_history}}

JSON: {{"scores":{{"R":0.0,"I":0.0,"A":0.0,"S":0.0,"E":0.0,"C":0.0}},"riasec_code":"XYZ","top_groups":["X","Y"],"confidence":0.0,"reasoning":"...","description":"...","suggested_majors":[{{"group":"...","majors":["..."],"fit_reason":"..."}}]}}"""


def _keyword_extract_signal(answer: str) -> dict:
    answer_lower = answer.lower()
    signals = {}
    for group, keywords in RIASEC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in answer_lower)
        signals[group] = min(score, 3)
    return signals


async def generate_greeting() -> str:
    """Tạo tình huống đầu tiên bằng Gemini để tự nhiên, nếu lỗi thì dùng fallback cố định."""
    if settings.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel(settings.GEMINI_MODEL, system_instruction=SYSTEM_INSTRUCTION_AGENT)
            response = await model.generate_content_async(
                "Tạo một tình huống mở đầu để bắt đầu trò chuyện hướng nghiệp với học sinh. Tình huống này nên mở và bao quát, không quá thiên về một nhóm cụ thể."
            )
            text = response.text.strip()
            if len(text) > 20:
                return text
        except Exception as e:
            logger.error(f"Gemini generate_greeting error: {e}")
            
    return FIXED_FIRST_SCENARIO


async def generate_question(
    question_no: int,
    target_groups: list,
    saturated_groups: list,
    history: list,
    groups_asked: dict = None,
) -> str:
    """Yêu cầu Gemini tạo tình huống mới hoàn toàn tự do."""
    primary_target = target_groups[0] if target_groups else "R"

    if settings.GEMINI_API_KEY:
        try:
            user_instruction = (
                f"Đây là lượt hỏi số {question_no}.\n"
                f"Mục tiêu chính: Đặt một tình huống TỰ DO dựa trên BỘ 60 CÂU HỎI RIASEC để khám phá sự phù hợp với nhóm {primary_target}.\n"
                f"Các nhóm đã đủ thông tin (hạn chế xoáy vào): {', '.join(saturated_groups) if saturated_groups else 'Chưa có'}.\n"
                "Yêu cầu: Tình huống có thể kết hợp 1-3 nhóm RIASEC để người dùng lựa chọn. Đọc kỹ lịch sử hội thoại trên, KHÔNG lặp lại chủ đề hay bối cảnh đã dùng."
            )
            contents = []
            for msg in history:
                role = "model" if msg.role == "assistant" else "user"
                contents.append({"role": role, "parts": [msg.content]})
            contents.append({"role": "user", "parts": [user_instruction]})
            
            model = genai.GenerativeModel(settings.GEMINI_MODEL, system_instruction=SYSTEM_INSTRUCTION_AGENT)
            response = await model.generate_content_async(contents)
            text = response.text.strip()
            if len(text) > 20:
                return text
        except Exception as e:
            logger.error(f"Gemini generate_question error: {e}")

    # Fallback khi Gemini API lỗi
    return f"Câu trả lời của em giúp anh/chị hiểu thêm nhiều điều! Nếu em tham gia một hoạt động liên quan đến {primary_target}, em sẽ thích làm công việc cụ thể nào nhất?"


async def extract_signal(question: str, answer: str) -> dict:
    if not settings.GEMINI_API_KEY:
        return {"signals": _keyword_extract_signal(answer), "answer_quality": "clear"}
    prompt = EXTRACT_SIGNAL_PROMPT.format(question=question, answer=answer)
    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL, generation_config={"response_mime_type": "application/json"})
        response = await model.generate_content_async(prompt)
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini extract_signal error: {e}")
        return {"signals": _keyword_extract_signal(answer), "answer_quality": "clear"}


async def generate_final_scoring(history_text: str) -> dict:
    if not settings.GEMINI_API_KEY:
        return None
    prompt = SYSTEM_PROMPT_SCORING.format(conversation_history=history_text)
    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL, generation_config={"response_mime_type": "application/json"})
        response = await model.generate_content_async(prompt)
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini final_scoring error: {e}")
        return None
