from app.schemas.llm import FinalReportResult
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine


CAREER_GROUPS = {
    "R": ["Kỹ thuật", "Cơ khí", "Điện - điện tử", "Tự động hóa", "Công nghệ vận hành", "Robot"],
    "I": ["Công nghệ thông tin", "Khoa học dữ liệu", "AI", "Y sinh", "Nghiên cứu", "An toàn thông tin"],
    "A": ["Thiết kế", "Truyền thông", "Nội dung số", "Mỹ thuật ứng dụng", "UX/UI", "Marketing sáng tạo"],
    "S": ["Giáo dục", "Tâm lý học", "Công tác xã hội", "Y tế cộng đồng", "Tư vấn học đường"],
    "E": ["Kinh doanh", "Marketing", "Quản trị", "Quan hệ công chúng", "Khởi nghiệp", "Quản lý dự án"],
    "C": ["Kế toán", "Tài chính", "Phân tích nghiệp vụ", "Hành chính", "Quản trị dữ liệu", "Kiểm toán"],
}

DIGITAL_COMPETENCIES = {
    "R": ["Tư duy kỹ thuật", "Vận hành công cụ số", "Đọc hiểu tài liệu kỹ thuật", "Thử nghiệm sản phẩm"],
    "I": ["Phân tích dữ liệu", "Tư duy logic", "Tìm kiếm và đánh giá thông tin", "Tư duy nghiên cứu"],
    "A": ["Sáng tạo nội dung số", "Thiết kế trải nghiệm", "Kể chuyện bằng dữ liệu", "Tư duy hình ảnh"],
    "S": ["Giao tiếp số", "Hỗ trợ người dùng", "Làm việc nhóm trực tuyến", "Lắng nghe và phản hồi"],
    "E": ["Quản lý dự án số", "Thuyết trình", "Tư duy sản phẩm", "Đàm phán và thuyết phục"],
    "C": ["Quản lý dữ liệu", "Tự động hóa quy trình", "Kiểm soát chất lượng thông tin", "Tổ chức tài liệu"],
}

RECOMMENDED_MAJORS = {
    "R": [
        "Công nghệ kỹ thuật cơ khí",
        "Kỹ thuật điện",
        "Tự động hóa",
        "Cơ điện tử",
        "Kỹ thuật robot",
    ],
    "I": [
        "Công nghệ thông tin",
        "Khoa học dữ liệu",
        "Trí tuệ nhân tạo",
        "An toàn thông tin",
        "Kỹ thuật phần mềm",
        "Hệ thống thông tin",
    ],
    "A": [
        "Thiết kế đồ họa",
        "Truyền thông đa phương tiện",
        "Thiết kế UX/UI",
        "Marketing sáng tạo",
        "Công nghệ truyền thông",
    ],
    "S": [
        "Sư phạm",
        "Tâm lý học",
        "Công tác xã hội",
        "Quản trị nhân lực",
        "Y tế công cộng",
    ],
    "E": [
        "Quản trị kinh doanh",
        "Marketing",
        "Thương mại điện tử",
        "Kinh doanh quốc tế",
        "Quan hệ công chúng",
        "Quản lý dự án",
    ],
    "C": [
        "Kế toán",
        "Tài chính ngân hàng",
        "Kiểm toán",
        "Hệ thống thông tin quản lý",
        "Phân tích nghiệp vụ",
        "Quản trị văn phòng",
    ],
}

SUITABLE_ROLES = {
    "R": ["Kỹ thuật viên", "Kỹ sư vận hành", "Kỹ sư tự động hóa", "Nhân sự thử nghiệm sản phẩm"],
    "I": ["Backend Developer", "Data Analyst", "AI Engineer", "Security Analyst", "Research Assistant"],
    "A": ["UX/UI Designer", "Content Creator", "Graphic Designer", "Creative Marketer"],
    "S": ["Giáo viên", "Chuyên viên tư vấn", "HR Executive", "Customer Success"],
    "E": ["Product Manager", "Sales Executive", "Marketing Executive", "Business Developer", "Project Coordinator"],
    "C": ["Business Analyst", "Data Administrator", "Kế toán viên", "Kiểm toán viên", "Operations Executive"],
}


class ReportService:
    def __init__(self):
        self.prompt_engine = PromptEngine()
        self.llm_client = LLMClient()

    async def build_summary_with_llm(
        self,
        history: list[dict],
        scores: dict,
        confidence: dict,
        riasec_code: str,
    ) -> str:
        career_groups = self.build_career_groups(riasec_code)
        recommended_majors = self.build_recommended_majors(riasec_code)
        suitable_roles = self.build_suitable_roles(riasec_code)
        digital_competencies = self.build_digital_competencies(riasec_code)

        prompt = self.prompt_engine.build_final_report_prompt(
            history=history,
            scores=scores,
            confidence=confidence,
            riasec_code=riasec_code,
            career_groups=career_groups,
            recommended_majors=recommended_majors,
            suitable_roles=suitable_roles,
            digital_competencies=digital_competencies,
        )

        try:
            data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=FinalReportResult,
                temperature=0.4,
            )

            result = FinalReportResult.model_validate(data)

            strengths = ", ".join(result.strengths[:4])
            career_text = ", ".join(result.suitable_career_groups[:5] or career_groups[:5])
            major_text = ", ".join(result.recommended_majors[:6] or recommended_majors[:6])
            role_text = ", ".join(result.suitable_roles[:5] or suitable_roles[:5])
            learning_text = ", ".join(result.learning_suggestions[:4])

            return (
                f"{result.summary} "
                f"Điểm mạnh nổi bật: {strengths}. "
                f"Nhóm ngành phù hợp: {career_text}. "
                f"Ngành học có thể tham khảo: {major_text}. "
                f"Vai trò nghề nghiệp phù hợp: {role_text}. "
                f"Kỹ năng nên phát triển thêm: {learning_text}."
            )

        except Exception:
            return self.build_summary(
                riasec_code=riasec_code,
                scores=scores,
            )

    def build_career_groups(self, riasec_code: str) -> list[str]:
        return self._unique_items_for_code(CAREER_GROUPS, riasec_code)

    def build_digital_competencies(self, riasec_code: str) -> dict:
        return {
            group: DIGITAL_COMPETENCIES.get(group, [])
            for group in riasec_code
        }

    def build_recommended_majors(self, riasec_code: str) -> list[str]:
        return self._unique_items_for_code(RECOMMENDED_MAJORS, riasec_code)

    def build_suitable_roles(self, riasec_code: str) -> list[str]:
        return self._unique_items_for_code(SUITABLE_ROLES, riasec_code)

    def _unique_items_for_code(
        self,
        mapping: dict[str, list[str]],
        riasec_code: str,
    ) -> list[str]:
        items = []

        for group in riasec_code:
            items.extend(mapping.get(group, []))

        return list(dict.fromkeys(items))

    def build_summary(self, riasec_code: str, scores: dict) -> str:
        top = riasec_code[:3]
        career_groups = self.build_career_groups(top)[:6]
        majors = self.build_recommended_majors(top)[:6]
        roles = self.build_suitable_roles(top)[:6]

        return (
            f"Kết quả hiện tại cho thấy bạn nổi bật ở nhóm {top}. "
            f"Bạn có xu hướng phù hợp với các hoạt động liên quan đến {', '.join(career_groups)}. "
            f"Một số ngành học có thể tham khảo gồm {', '.join(majors)}. "
            f"Các vai trò nghề nghiệp phù hợp có thể là {', '.join(roles)}. "
            f"Kết quả này là gợi ý định hướng ban đầu, nên kết hợp thêm học lực, sở thích thực tế và mục tiêu cá nhân."
        )
