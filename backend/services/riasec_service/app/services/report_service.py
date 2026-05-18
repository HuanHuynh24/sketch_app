from app.core.config import settings
from app.core.constants import RIASEC_GROUPS
from app.schemas.llm import FinalReportResult
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine
from app.services.riasec_knowledge import RIASEC_GROUP_PROFILES


DEFAULT_LIMITS = {
    "career_groups": 5,
    "recommended_majors": 8,
    "suitable_roles": 5,
}


class ReportService:
    def __init__(self, enable_llm: bool = True):
        self.prompt_engine = PromptEngine()
        self.llm_client = LLMClient() if enable_llm else None

    async def build_summary_with_llm(
        self,
        history: list[dict],
        scores: dict,
        confidence: dict,
        riasec_code: str,
    ) -> str:
        career_groups = self.build_career_groups(
            riasec_code,
            scores=scores,
            confidence=confidence,
        )
        recommended_majors = self.build_recommended_majors(
            riasec_code,
            scores=scores,
            confidence=confidence,
        )
        suitable_roles = self.build_suitable_roles(
            riasec_code,
            scores=scores,
            confidence=confidence,
        )
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
            if not self.llm_client:
                raise RuntimeError("LLM client is disabled")

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

    def build_career_groups(
        self,
        riasec_code: str,
        scores: dict | None = None,
        confidence: dict | None = None,
        limit: int | None = None,
    ) -> list[str]:
        return self._rank_items_for_code(
            "career_groups",
            riasec_code,
            scores=scores,
            confidence=confidence,
            limit=limit or DEFAULT_LIMITS["career_groups"],
        )

    def build_digital_competencies(self, riasec_code: str) -> dict:
        return {
            group: RIASEC_GROUP_PROFILES.get(group, {}).get("digital_competencies", [])
            for group in riasec_code
        }

    def build_recommended_majors(
        self,
        riasec_code: str,
        scores: dict | None = None,
        confidence: dict | None = None,
        limit: int | None = None,
    ) -> list[str]:
        return self._rank_items_for_code(
            "recommended_majors",
            riasec_code,
            scores=scores,
            confidence=confidence,
            limit=limit or DEFAULT_LIMITS["recommended_majors"],
        )

    def build_suitable_roles(
        self,
        riasec_code: str,
        scores: dict | None = None,
        confidence: dict | None = None,
        limit: int | None = None,
    ) -> list[str]:
        return self._rank_items_for_code(
            "suitable_roles",
            riasec_code,
            scores=scores,
            confidence=confidence,
            limit=limit or DEFAULT_LIMITS["suitable_roles"],
        )

    def build_result_payload(
        self,
        scores: dict,
        confidence: dict,
        riasec_code: str,
    ) -> dict:
        return {
            "radar_chart": self.build_radar_chart(scores, confidence),
            "dominant_groups": self.build_dominant_groups(scores, confidence),
            "group_analysis": self.build_group_analysis(scores, confidence),
            "career_recommendations": self.build_ranked_career_recommendations(
                riasec_code,
                scores=scores,
                confidence=confidence,
            ),
        }

    def build_radar_chart(self, scores: dict, confidence: dict) -> dict:
        max_value = max(settings.MAX_RIASEC_STEPS * 2, 1)

        axes = []
        for group, profile in RIASEC_GROUP_PROFILES.items():
            raw_score = round(float(scores.get(group, 0)), 4)
            confidence_value = round(float(confidence.get(group, 0)), 4)

            axes.append(
                {
                    "group": group,
                    "label": profile["label"],
                    "score": raw_score,
                    "max_score": max_value,
                    "normalized_score": round((raw_score / max_value) * 100, 2),
                    "confidence": confidence_value,
                    "description": profile["description"],
                }
            )

        return {
            "type": "riasec_radar",
            "max_score": max_value,
            "axes": axes,
        }

    def build_dominant_groups(
        self,
        scores: dict,
        confidence: dict,
        top_n: int = 3,
    ) -> list[dict]:
        sorted_groups = self._sort_groups_by_score(scores)

        return [
            {
                "group": group,
                "label": RIASEC_GROUP_PROFILES[group]["label"],
                "score": round(score, 4),
                "confidence": round(float(confidence.get(group, 0)), 4),
                "description": RIASEC_GROUP_PROFILES[group]["description"],
            }
            for group, score in sorted_groups[:top_n]
        ]

    def build_group_analysis(self, scores: dict, confidence: dict) -> list[dict]:
        analysis = []

        for group, score in self._sort_groups_by_score(scores):
            profile = RIASEC_GROUP_PROFILES[group]
            level = self._score_level(score)

            analysis.append(
                {
                    "group": group,
                    "name": profile["name"],
                    "label": profile["label"],
                    "score": round(score, 4),
                    "confidence": round(float(confidence.get(group, 0)), 4),
                    "level": level,
                    "description": profile["description"],
                    "career_groups": profile["career_groups"],
                    "recommended_majors": profile["recommended_majors"],
                    "suitable_roles": profile["suitable_roles"],
                    "digital_competencies": profile["digital_competencies"],
                }
            )

        return analysis

    def build_career_recommendations(self, riasec_code: str) -> dict:
        return {
            "riasec_code": riasec_code,
            "career_groups": self.build_career_groups(riasec_code),
            "recommended_majors": self.build_recommended_majors(riasec_code),
            "suitable_roles": self.build_suitable_roles(riasec_code),
            "digital_competencies": self.build_digital_competencies(riasec_code),
        }

    def build_ranked_career_recommendations(
        self,
        riasec_code: str,
        scores: dict,
        confidence: dict,
    ) -> dict:
        return {
            "riasec_code": riasec_code,
            "career_groups": self.build_career_groups(
                riasec_code,
                scores=scores,
                confidence=confidence,
            ),
            "recommended_majors": self.build_recommended_majors(
                riasec_code,
                scores=scores,
                confidence=confidence,
            ),
            "suitable_roles": self.build_suitable_roles(
                riasec_code,
                scores=scores,
                confidence=confidence,
            ),
            "digital_competencies": self.build_digital_competencies(riasec_code),
        }

    def _rank_items_for_code(
        self,
        field_name: str,
        riasec_code: str,
        scores: dict | None = None,
        confidence: dict | None = None,
        limit: int = 8,
    ) -> list[str]:
        candidate_scores: dict[str, float] = {}
        candidate_sources: dict[str, set[str]] = {}
        valid_code = [
            group
            for group in riasec_code
            if group in RIASEC_GROUPS
        ]

        if not valid_code:
            valid_code = RIASEC_GROUPS[:3]

        for code_position, group in enumerate(valid_code):
            profile = RIASEC_GROUP_PROFILES.get(group, {})
            items = profile.get(field_name, [])
            group_score = float((scores or {}).get(group, 1))
            group_confidence = float((confidence or {}).get(group, 0.6))
            code_weight = max(1.0, len(valid_code) - code_position)
            group_weight = max(group_score, 0.5) * max(group_confidence, 0.35)

            for item_position, item in enumerate(items):
                item_weight = 1 / (1 + item_position * 0.08)
                candidate_scores[item] = candidate_scores.get(item, 0) + (
                    code_weight * group_weight * item_weight
                )
                candidate_sources.setdefault(item, set()).add(group)

        ranked_items = sorted(
            candidate_scores.items(),
            key=lambda item: (
                item[1],
                len(candidate_sources.get(item[0], set())),
                -len(item[0]),
            ),
            reverse=True,
        )

        return [
            item
            for item, _score in ranked_items[:limit]
        ]

    def _sort_groups_by_score(self, scores: dict) -> list[tuple[str, float]]:
        return sorted(
            [
                (group, float(scores.get(group, 0)))
                for group in RIASEC_GROUP_PROFILES
            ],
            key=lambda item: item[1],
            reverse=True,
        )

    def _score_level(self, score: float) -> str:
        if score >= 8:
            return "high"

        if score >= 4:
            return "medium"

        if score > 0:
            return "emerging"

        return "low"

    def build_summary(self, riasec_code: str, scores: dict) -> str:
        top = riasec_code[:3]
        career_groups = self.build_career_groups(top, scores=scores, limit=5)
        majors = self.build_recommended_majors(top, scores=scores, limit=6)
        roles = self.build_suitable_roles(top, scores=scores, limit=5)

        return (
            f"Kết quả hiện tại cho thấy bạn nổi bật ở nhóm {top}. "
            f"Bạn có xu hướng phù hợp với các hoạt động liên quan đến {', '.join(career_groups)}. "
            f"Một số ngành học có thể tham khảo gồm {', '.join(majors)}. "
            f"Các vai trò nghề nghiệp phù hợp có thể là {', '.join(roles)}. "
            f"Kết quả này là gợi ý định hướng ban đầu, nên kết hợp thêm học lực, "
            f"sở thích thực tế và mục tiêu cá nhân."
        )
