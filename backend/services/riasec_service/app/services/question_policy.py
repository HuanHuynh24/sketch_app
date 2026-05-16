from app.core.constants import MESSAGE_ROLE_ASSISTANT


QUESTION_MESSAGE_TYPES = {"anchor_scenario", "adaptive_scenario"}


class QuestionPolicy:
    def find_last_question_message(self, history):
        for message in reversed(history):
            if (
                message.role == MESSAGE_ROLE_ASSISTANT
                and message.message_type in QUESTION_MESSAGE_TYPES
            ):
                return message

        return None

    def build_history_payload(self, history) -> list[dict]:
        return [
            {
                "role": message.role,
                "type": message.message_type,
                "content": message.content,
            }
            for message in history[-10:]
        ]

    def extract_asked_focus_groups(self, history) -> list[list[str]]:
        asked_focus_groups = []

        for message in history:
            if (
                message.role == MESSAGE_ROLE_ASSISTANT
                and message.message_type in QUESTION_MESSAGE_TYPES
                and message.metadata_json
            ):
                focus = message.metadata_json.get("focus_groups")

                if focus:
                    asked_focus_groups.append(sorted(focus))

        return asked_focus_groups

    def select_next_context(self, history) -> str:
        contexts = [
            "gian hàng trải nghiệm ngành nghề trong giờ ra chơi",
            "nhóm lớp chuẩn bị video ngắn giới thiệu một ngành học",
            "câu lạc bộ cần cứu một workshop sắp trễ deadline",
            "dự án khảo sát học sinh lớp 12 chọn ngành",
            "buổi demo sản phẩm học tập trước giáo viên",
            "chiến dịch truyền thông tuyển thành viên câu lạc bộ",
            "buổi tư vấn chọn ngành có phụ huynh cùng tham gia",
            "cuộc thi ý tưởng cải thiện không gian học tập",
            "nhóm trực sự kiện bị thiếu người vào phút cuối",
            "bản kế hoạch tham quan doanh nghiệp cần hoàn thiện gấp",
        ]

        history_text = self.assistant_history_text(history)

        for context in contexts:
            if context.lower() not in history_text:
                return context

        return contexts[len(history) % len(contexts)]

    def select_next_question_style(self, history) -> str:
        styles = [
            "trade_off",
            "role_choice",
            "next_action",
            "priority_ranking",
            "conflict_scenario",
            "reflection",
            "resource_constraint",
        ]

        used_styles = []

        for message in history:
            if (
                message.role == MESSAGE_ROLE_ASSISTANT
                and message.message_type in QUESTION_MESSAGE_TYPES
                and message.metadata_json
            ):
                style = message.metadata_json.get("question_style")
                if style:
                    used_styles.append(style)

        for style in styles:
            if style not in used_styles:
                return style

        return styles[len(used_styles) % len(styles)]

    def extract_banned_topics(self, history) -> list[str]:
        history_text = self.assistant_history_text(history)
        topic_keywords = [
            "lỗi hệ thống",
            "phân tích log",
            "hệ thống cảm biến",
            "cảm biến",
            "thiết bị hoạt động sai",
            "không gian học tập thông minh",
            "trong một hoạt động mới ở trường",
            "ngày hội hướng nghiệp của trường",
            "dự án nhóm trong lớp",
        ]

        return [
            keyword
            for keyword in topic_keywords
            if keyword in history_text
        ]

    def ensure_question_not_repeated(
        self,
        question_data: dict,
        history,
        focus_groups: list[str],
    ) -> dict | None:
        new_content = question_data.get("content", "").strip()

        if not new_content:
            return None

        new_lower = new_content.lower()
        previous_questions = [
            message.content.strip().lower()
            for message in history
            if (
                message.role == MESSAGE_ROLE_ASSISTANT
                and message.message_type in QUESTION_MESSAGE_TYPES
            )
        ]

        for topic in self.extract_banned_topics(history):
            if topic in new_lower:
                return None

        for old_content in previous_questions:
            if new_lower == old_content:
                return None

            if len(new_lower) > 100 and new_lower[:100] in old_content:
                return None

            if self.simple_text_similarity(new_lower, old_content) >= 0.75:
                return None

        question_data["focus_groups"] = question_data.get("focus_groups") or focus_groups
        question_data["type"] = question_data.get("type") or "adaptive_scenario"

        return question_data

    def assistant_history_text(self, history) -> str:
        return " ".join(
            [
                message.content.lower()
                for message in history
                if message.role == MESSAGE_ROLE_ASSISTANT
            ]
        )

    def simple_text_similarity(self, a: str, b: str) -> float:
        a_words = set(a.split())
        b_words = set(b.split())

        if not a_words or not b_words:
            return 0.0

        intersection = len(a_words.intersection(b_words))
        union = len(a_words.union(b_words))

        return intersection / union
