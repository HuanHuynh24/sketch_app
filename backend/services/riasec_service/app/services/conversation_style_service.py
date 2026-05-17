from app.core.constants import RIASEC_GROUPS


GROUP_LABELS = {
    "R": "thực hành và xử lý việc cụ thể",
    "I": "phân tích và tìm nguyên nhân",
    "A": "ý tưởng và cách thể hiện sáng tạo",
    "S": "hỗ trợ và kết nối với người khác",
    "E": "chủ động dẫn dắt và thuyết phục",
    "C": "sắp xếp, kiểm tra và làm theo kế hoạch",
}


class ConversationStyleService:
    def build_opening_messages(self) -> list[dict]:
        return [
            {
                "content": (
                    "Chào bạn, mình sẽ hỏi vài tình huống ngắn để hiểu cách bạn "
                    "thường chọn hành động trong học tập và hoạt động nhóm."
                ),
                "message_type": "intro",
                "metadata_json": {"tone": "welcome"},
            },
            {
                "content": (
                    "Không có đáp án đúng sai đâu. Bạn cứ trả lời tự nhiên theo "
                    "cách bạn thật sự sẽ làm nhé."
                ),
                "message_type": "intro",
                "metadata_json": {"tone": "reassurance"},
            },
            {
                "content": "Mình bắt đầu bằng một tình huống đầu tiên nhé:",
                "message_type": "question_lead_in",
                "metadata_json": {"question_position": "first"},
            },
        ]

    def build_transition_message(
        self,
        scoring_result,
        current_step: int,
        max_steps: int,
    ) -> dict:
        if current_step >= max_steps - 1:
            content = (
                "Sắp xong rồi. Mình hỏi thêm một tình huống cuối để kết quả chắc hơn nhé."
            )
        else:
            primary_groups = self._primary_groups(scoring_result)
            if primary_groups:
                labels = [
                    GROUP_LABELS[group]
                    for group in primary_groups
                    if group in GROUP_LABELS
                ]
                content = (
                    "Mình ghi nhận cách bạn xử lý tình huống này. "
                    f"Câu trả lời vừa rồi có vài tín hiệu ở các xu hướng: {self._join_labels(labels)}. "
                    "Giờ mình đổi sang một bối cảnh khác một chút nhé:"
                )
            else:
                content = (
                    "Mình ghi nhận câu trả lời của bạn rồi. "
                    "Giờ mình hỏi tiếp một tình huống khác để hiểu rõ hơn cách bạn ưu tiên nhé:"
                )

        return {
            "content": content,
            "message_type": "transition",
            "metadata_json": {
                "step": current_step,
                "primary_groups": self._primary_groups(scoring_result),
            },
        }

    def build_invalid_answer_lead_in(self) -> dict:
        return {
            "content": (
                "Mình chưa đủ thông tin để hiểu lựa chọn của bạn trong tình huống này."
            ),
            "message_type": "answer_reflection",
            "metadata_json": {"quality": "invalid"},
        }

    def build_completion_lead_in(self, riasec_code: str | None) -> dict:
        content = "Cảm ơn bạn. Mình đã có đủ dữ liệu để tổng hợp xu hướng RIASEC của bạn."

        if riasec_code:
            content += f" Mã nổi bật hiện tại là {riasec_code}."

        return {
            "content": content,
            "message_type": "completion_lead_in",
            "metadata_json": {"riasec_code": riasec_code},
        }

    def _primary_groups(self, scoring_result) -> list[str]:
        return [
            group
            for group in getattr(scoring_result, "primary_groups", [])
            if group in RIASEC_GROUPS
        ][:3]

    def _join_labels(self, labels: list[str]) -> str:
        if not labels:
            return "cách bạn ra quyết định"

        if len(labels) == 1:
            return labels[0]

        return ", ".join(labels[:-1]) + f" và {labels[-1]}"
