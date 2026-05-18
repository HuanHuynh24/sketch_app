import logging

from app.schemas.llm import GeneratedQuestion
from app.services.fallback_questions import select_fallback_question
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine
from app.services.question_policy import QuestionPolicy
from app.services.riasec_knowledge import RIASEC_GROUP_PROFILES


logger = logging.getLogger(__name__)


class QuestionGenerationService:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompt_engine = PromptEngine()
        self.policy = QuestionPolicy()

    async def generate_anchor_question(self) -> dict:
        prompt = self.prompt_engine.build_anchor_prompt()

        try:
            question_data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=GeneratedQuestion,
                temperature=0.75,
            )
        except Exception:
            logger.exception("Gemini anchor question generation failed; using fallback")
            question_data = {
                "type": "anchor_scenario",
                "content": (
                    "Gian hàng hướng nghiệp của lớp sắp mở cửa nhưng mọi thứ còn khá rối: poster chưa xong, "
                    "thông tin ngành còn thiếu, bàn trải nghiệm chưa thử và nhóm chưa phân công rõ. "
                    "Nếu em chỉ kịp nhận một phần quan trọng nhất, em sẽ làm gì trước và vì sao?"
                ),
                "focus_groups": ["R", "I", "A", "S", "E", "C"],
                "context": "anchor",
                "question_style": "role_choice",
            }

        return self.normalize_question_data(
            question_data=question_data,
            default_type="anchor_scenario",
            focus_groups=["R", "I", "A", "S", "E", "C"],
            fallback_context="anchor",
            fallback_style="role_choice",
        )

    async def generate_adaptive_question(
        self,
        history,
        scores: dict,
        confidence: dict,
        focus_groups: list[str],
        question_number: int,
    ) -> dict:
        history_payload = self.policy.build_history_payload(history)
        suggested_context = self.policy.select_next_context(history)
        banned_topics = self.policy.extract_banned_topics(history)
        question_style = self.policy.select_next_question_style(history)

        prompt = self.prompt_engine.build_adaptive_prompt(
            history=history_payload,
            scores=scores,
            confidence=confidence,
            focus_groups=focus_groups,
            suggested_context=suggested_context,
            banned_topics=banned_topics,
            question_number=question_number,
            question_style=question_style,
        )

        try:
            question_data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=GeneratedQuestion,
                temperature=0.78,
            )

            question_data = self.normalize_question_data(
                question_data=question_data,
                default_type="adaptive_scenario",
                focus_groups=focus_groups,
                fallback_context=suggested_context,
                fallback_style=question_style,
            )

            non_repeated_question = self.policy.ensure_question_not_repeated(
                question_data=question_data,
                history=history,
                focus_groups=focus_groups,
            )

            if non_repeated_question:
                return non_repeated_question

        except Exception:
            logger.exception("Gemini adaptive question generation failed; using fallback")

        return self.fallback_adaptive_question(
            focus_groups=focus_groups,
            history=history,
            context=suggested_context,
            question_style=question_style,
        )

    def normalize_question_data(
        self,
        question_data: dict,
        default_type: str,
        focus_groups: list[str],
        fallback_context: str | None = None,
        fallback_style: str | None = None,
    ) -> dict:
        content = str(question_data.get("content", "")).strip()

        if not content:
            content = (
                "Em đang ở một hoạt động hướng nghiệp có deadline gấp và nhóm cần chọn người xử lý phần quan trọng nhất. "
                "Em muốn nhận phần việc nào, em sẽ bắt đầu ra sao và vì sao?"
            )

        normalized_focus_groups = [
            str(group)
            for group in (question_data.get("focus_groups") or focus_groups)
            if str(group) in RIASEC_GROUP_PROFILES
        ] or focus_groups

        expected_signals = question_data.get("expected_signals") or {
            group: RIASEC_GROUP_PROFILES.get(group, {}).get(
                "assessment_indicators",
                [],
            )[:3]
            for group in normalized_focus_groups
        }

        scoring_rubric = question_data.get("scoring_rubric") or {
            "strong": "Có hành động cụ thể, lý do rõ, và bằng chứng hành vi khớp nhóm.",
            "weak": "Chỉ nêu sở thích chung hoặc chọn hướng nhưng chưa giải thích.",
            "clarify": "Trả lời chung chung, chọn nhiều hướng mà không nêu ưu tiên.",
        }

        return {
            "type": question_data.get("type") or default_type,
            "content": content,
            "focus_groups": normalized_focus_groups,
            "context": question_data.get("context") or fallback_context,
            "question_style": question_data.get("question_style") or fallback_style,
            "expected_signals": expected_signals,
            "scoring_rubric": scoring_rubric,
        }

    def fallback_adaptive_question(
        self,
        focus_groups: list[str],
        history,
        context: str | None = None,
        question_style: str | None = None,
    ) -> dict:
        content = select_fallback_question(
            focus_groups=focus_groups,
            history_text=self.policy.assistant_history_text(history),
        )

        return {
            "type": "adaptive_scenario",
            "content": content,
            "focus_groups": focus_groups,
            "context": context,
            "question_style": question_style,
            "expected_signals": {
                group: RIASEC_GROUP_PROFILES.get(group, {}).get(
                    "assessment_indicators",
                    [],
                )[:3]
                for group in focus_groups
            },
            "scoring_rubric": {
                "strong": "Có hành động cụ thể, lý do rõ, và bằng chứng hành vi khớp nhóm.",
                "weak": "Chỉ nêu sở thích chung hoặc chọn hướng nhưng chưa giải thích.",
                "clarify": "Trả lời chung chung, chọn nhiều hướng mà không nêu ưu tiên.",
            },
        }
