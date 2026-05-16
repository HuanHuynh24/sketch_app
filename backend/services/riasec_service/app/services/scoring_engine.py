import logging

from app.core.constants import RIASEC_GROUPS
from app.schemas.scoring import RiasecEvidence, RiasecScoringResult, RiasecScore
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine


logger = logging.getLogger(__name__)


RIASEC_KEYWORDS = {
    "R": [
        "máy móc",
        "thiết bị",
        "lắp đặt",
        "sửa chữa",
        "vận hành",
        "thực hành",
        "kỹ thuật",
        "công cụ",
    ],
    "I": [
    "phân tích",
    "dữ liệu",
    "logic",
    "nghiên cứu",
    "tìm hiểu",
    "so sánh",
    "đánh giá",
    "kiểm chứng",
    "giả thuyết",
    "bằng chứng",
],
    "A": [
        "sáng tạo",
        "thiết kế",
        "ý tưởng",
        "nội dung",
        "mỹ thuật",
        "hình ảnh",
        "truyền thông sáng tạo",
    ],
    "S": [
        "giúp đỡ",
        "hỗ trợ",
        "tư vấn",
        "hướng dẫn",
        "giảng dạy",
        "lắng nghe",
        "kết nối",
    ],
    "E": [
        "quản lý",
        "lãnh đạo",
        "thuyết phục",
        "kinh doanh",
        "đàm phán",
        "điều phối nhóm",
        "khởi nghiệp",
    ],
    "C": [
    "quy trình",
    "kế hoạch",
    "sắp xếp",
    "kiểm tra",
    "chính xác",
    "hồ sơ",
    "báo cáo",
    "theo dõi",
    "checklist",
    "phân loại",
    "chuẩn hóa",
],
}


class ScoringEngine:
    def __init__(self):
        self.prompt_engine = PromptEngine()
        self.llm_client = LLMClient()

    async def score_answer(
        self,
        scenario: str,
        answer_text: str,
    ) -> RiasecScoringResult:
        try:
            return await self.score_answer_with_llm(
                scenario=scenario,
                answer_text=answer_text,
            )
        except Exception:
            logger.exception(
                "Gemini scoring failed; falling back to rule-based scoring"
            )
            return self.score_answer_rule_based(answer_text)

    async def score_answer_with_llm(
        self,
        scenario: str,
        answer_text: str,
    ) -> RiasecScoringResult:
        prompt = self.prompt_engine.build_scoring_prompt(
            scenario=scenario,
            answer_text=answer_text,
        )

        data = await self.llm_client.generate_json(
            prompt=prompt,
            schema=RiasecScoringResult,
            temperature=0.2,
        )

        result = RiasecScoringResult.model_validate(data)

        cleaned_scores = {
            group: self._clamp(float(getattr(result.scores, group)), 0, 2)
            for group in RIASEC_GROUPS
        }

        cleaned_confidence = {
            group: self._clamp(float(getattr(result.confidence, group)), 0, 1)
            for group in RIASEC_GROUPS
        }

        return RiasecScoringResult(
            scores=RiasecScore(**cleaned_scores),
            confidence=RiasecScore(**cleaned_confidence),
            reasoning=result.reasoning,
            detected_traits=result.detected_traits,
            primary_groups=self._normalize_primary_groups(
                primary_groups=result.primary_groups,
                scores=cleaned_scores,
            ),
            evidence=self._clean_evidence(result.evidence),
        )

    def score_answer_rule_based(self, answer_text: str) -> RiasecScoringResult:
        text = answer_text.lower()

        scores = {key: 0.0 for key in RIASEC_GROUPS}
        detected_traits = []

        for group, keywords in RIASEC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[group] += 0.5
                    detected_traits.append(keyword)

        scores = {
            key: min(value, 2.0)
            for key, value in scores.items()
        }

        confidence = {
            key: min(scores[key] / 2.0, 1.0)
            for key in RIASEC_GROUPS
        }

        primary_groups = self._normalize_primary_groups(
            primary_groups=[],
            scores=scores,
        )

        evidence = [
            RiasecEvidence(
                group=group,
                quote=", ".join(detected_traits[:3]) or None,
                strength=scores[group],
                confidence=confidence[group],
            )
            for group in primary_groups
            if scores[group] > 0
        ]

        return RiasecScoringResult(
            scores=RiasecScore(**scores),
            confidence=RiasecScore(**confidence),
            reasoning="Fallback rule-based scoring do Gemini không khả dụng hoặc trả dữ liệu không hợp lệ.",
            detected_traits=list(set(detected_traits)),
            primary_groups=primary_groups,
            evidence=evidence,
        )

    def merge_scores(
        self,
        current_scores: dict,
        new_scores: dict,
        weight: float = 1.0,
    ) -> dict:
        merged = {}

        for group in RIASEC_GROUPS:
            merged[group] = round(
                float(current_scores.get(group, 0)) + float(new_scores.get(group, 0)) * weight,
                4,
            )

        return merged

    def merge_confidence(
        self,
        current_confidence: dict,
        new_confidence: dict,
        current_step: int,
    ) -> dict:
        merged = {}

        for group in RIASEC_GROUPS:
            old = float(current_confidence.get(group, 0))
            new = float(new_confidence.get(group, 0))

            merged[group] = round(
                ((old * current_step) + new) / max(current_step + 1, 1),
                4,
            )

        return merged

    def normalize_scores_to_100(self, scores: dict) -> dict:
        total = sum(float(v) for v in scores.values())

        if total <= 0:
            return {key: 0 for key in RIASEC_GROUPS}

        return {
            key: round((float(value) / total) * 100, 2)
            for key, value in scores.items()
        }

    def _clamp(self, value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(value, max_value))

    def _normalize_primary_groups(
        self,
        primary_groups: list[str],
        scores: dict,
    ) -> list[str]:
        valid_groups = [
            group
            for group in primary_groups
            if group in RIASEC_GROUPS
        ]

        if valid_groups:
            return valid_groups[:3]

        return [
            group
            for group, score in sorted(
                scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            if score > 0
        ][:3]

    def _clean_evidence(self, evidence: list[RiasecEvidence]) -> list[RiasecEvidence]:
        cleaned = []

        for item in evidence:
            if item.group not in RIASEC_GROUPS:
                continue

            cleaned.append(
                RiasecEvidence(
                    group=item.group,
                    quote=item.quote,
                    strength=self._clamp(float(item.strength), 0, 2),
                    confidence=self._clamp(float(item.confidence), 0, 1),
                )
            )

        return cleaned
