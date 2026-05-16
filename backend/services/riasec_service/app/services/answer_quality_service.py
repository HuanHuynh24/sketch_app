from app.schemas.llm import AnswerQualityResult
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine


LOCAL_INVALID_PHRASES = {
    "ok",
    "oke",
    "ừ",
    "ừm",
    "không biết",
    "ko biết",
    "k biết",
    "sao cũng được",
    "tùy",
    "abc",
    "test",
    "haha",
    "hehe",
    "...",
}


class AnswerQualityService:
    def __init__(self):
        self.prompt_engine = PromptEngine()
        self.llm_client = LLMClient()

    async def validate(
        self,
        scenario: str,
        answer_text: str,
    ) -> dict:
        text = answer_text.strip()

        if len(text) < 8:
            return {
                "is_valid": False,
                "reason": "Câu trả lời quá ngắn để đánh giá.",
                "warning_message": (
                    "Câu trả lời của bạn quá ngắn nên hệ thống chưa thể đánh giá. "
                    "Hãy nói rõ bạn sẽ chọn hướng nào và vì sao."
                ),
            }

        if text.lower() in LOCAL_INVALID_PHRASES:
            return {
                "is_valid": False,
                "reason": "Câu trả lời không nghiêm túc hoặc không đủ thông tin.",
                "warning_message": (
                    "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm. "
                    "Hãy trả lời nghiêm túc hơn bằng cách nói bạn sẽ chọn hướng nào và vì sao."
                ),
            }

        prompt = self.prompt_engine.build_answer_quality_prompt(
            scenario=scenario,
            answer_text=answer_text,
        )

        try:
            data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=AnswerQualityResult,
                temperature=0.1,
            )

            result = AnswerQualityResult.model_validate(data)

            if result.is_valid:
                return {
                    "is_valid": True,
                    "reason": result.reason,
                    "warning_message": None,
                }

            return {
                "is_valid": False,
                "reason": result.reason,
                "warning_message": result.warning_message
                or (
                    "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm. "
                    "Hãy nói rõ bạn sẽ chọn hướng nào và vì sao."
                ),
            }

        except Exception:
            return {
                "is_valid": True,
                "reason": "Quality check fallback passed.",
                "warning_message": None,
            }
