import logging

from app.core.constants import RIASEC_GROUPS
from app.schemas.scoring import RiasecEvidence, RiasecScoringResult, RiasecScore
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine
from app.services.riasec_knowledge import RIASEC_GROUP_PROFILES


logger = logging.getLogger(__name__)


class ScoringEngine:
    def __init__(self):
        self.prompt_engine = PromptEngine()
        self.llm_client = LLMClient()

    async def score_answer(
        self,
        scenario: str,
        answer_text: str,
        focus_groups: list[str] | None = None,
        question_metadata: dict | None = None,
    ) -> RiasecScoringResult:
        try:
            return await self.score_answer_with_llm(
                scenario=scenario,
                answer_text=answer_text,
                focus_groups=focus_groups,
                question_metadata=question_metadata,
            )
        except Exception:
            logger.exception(
                "Gemini scoring failed; falling back to rule-based scoring"
            )
            return self.score_answer_rule_based(
                answer_text=answer_text,
                focus_groups=focus_groups,
            )

    async def score_answer_with_llm(
        self,
        scenario: str,
        answer_text: str,
        focus_groups: list[str] | None = None,
        question_metadata: dict | None = None,
    ) -> RiasecScoringResult:
        question_metadata = question_metadata or {}
        focus_groups = self._normalize_focus_groups(focus_groups or [])
        prompt = self.prompt_engine.build_scoring_prompt(
            scenario=scenario,
            answer_text=answer_text,
            focus_groups=focus_groups,
            expected_signals=question_metadata.get("expected_signals"),
            scoring_rubric=question_metadata.get("scoring_rubric"),
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

        cleaned_evidence = self._clean_evidence(result.evidence)
        guarded_scores, guarded_confidence, guarded_evidence = (
            self._apply_evidence_guards(
                scores=cleaned_scores,
                confidence=cleaned_confidence,
                evidence=cleaned_evidence,
                focus_groups=focus_groups,
                answer_text=answer_text,
            )
        )

        return RiasecScoringResult(
            scores=RiasecScore(**guarded_scores),
            confidence=RiasecScore(**guarded_confidence),
            reasoning=result.reasoning,
            detected_traits=result.detected_traits,
            primary_groups=self._normalize_primary_groups(
                primary_groups=result.primary_groups,
                scores=guarded_scores,
            ),
            evidence=guarded_evidence,
        )

    def score_answer_rule_based(
        self,
        answer_text: str,
        focus_groups: list[str] | None = None,
    ) -> RiasecScoringResult:
        text = answer_text.lower()
        focus_groups = self._normalize_focus_groups(focus_groups or [])

        scores = {key: 0.0 for key in RIASEC_GROUPS}
        detected_traits_by_group = {key: [] for key in RIASEC_GROUPS}

        for group, profile in RIASEC_GROUP_PROFILES.items():
            for keyword in profile["keywords"]:
                if keyword in text:
                    score_increment = 0.5 if not focus_groups or group in focus_groups else 0.25
                    scores[group] += score_increment
                    detected_traits_by_group[group].append(keyword)

        scores = {
            key: min(value, 2.0)
            for key, value in scores.items()
        }

        confidence = {
            key: min(scores[key] / 2.0, 0.75)
            for key in RIASEC_GROUPS
        }

        primary_groups = self._normalize_primary_groups(
            primary_groups=[],
            scores=scores,
        )

        evidence = [
            RiasecEvidence(
                group=group,
                quote=", ".join(detected_traits_by_group[group][:3]) or None,
                strength=scores[group],
                confidence=confidence[group],
            )
            for group in primary_groups
            if scores[group] > 0
        ]

        detected_traits = []
        for traits in detected_traits_by_group.values():
            detected_traits.extend(traits)

        return RiasecScoringResult(
            scores=RiasecScore(**scores),
            confidence=RiasecScore(**confidence),
            reasoning=(
                "Fallback rule-based scoring dựa trên bộ tín hiệu RIASEC nội bộ "
                "do Gemini không khả dụng hoặc trả dữ liệu không hợp lệ."
            ),
            detected_traits=list(dict.fromkeys(detected_traits)),
            primary_groups=primary_groups,
            evidence=evidence,
        )

    def merge_scores(
        self,
        current_scores: dict,
        new_scores: dict,
        new_confidence: dict | None = None,
        weight: float = 1.0,
    ) -> dict:
        merged = {}
        new_confidence = new_confidence or {}

        for group in RIASEC_GROUPS:
            confidence_weight = 0.5 + (
                self._clamp(float(new_confidence.get(group, 0.5)), 0, 1) * 0.5
            )
            merged[group] = round(
                float(current_scores.get(group, 0))
                + float(new_scores.get(group, 0)) * weight * confidence_weight,
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

    def _normalize_focus_groups(self, focus_groups: list[str]) -> list[str]:
        return [
            group
            for group in focus_groups
            if group in RIASEC_GROUPS
        ]

    def _apply_evidence_guards(
        self,
        scores: dict,
        confidence: dict,
        evidence: list[RiasecEvidence],
        focus_groups: list[str],
        answer_text: str,
    ) -> tuple[dict, dict, list[RiasecEvidence]]:
        evidence_by_group = {group: [] for group in RIASEC_GROUPS}

        for item in evidence:
            evidence_by_group[item.group].append(item)

        guarded_scores = {}
        guarded_confidence = {}

        for group in RIASEC_GROUPS:
            group_evidence = evidence_by_group[group]
            score = float(scores.get(group, 0))
            group_confidence = float(confidence.get(group, 0))

            if score <= 0:
                guarded_scores[group] = 0
                guarded_confidence[group] = 0
                continue

            if not group_evidence:
                guarded_scores[group] = 0
                guarded_confidence[group] = 0
                continue

            best_evidence = max(
                group_evidence,
                key=lambda item: (float(item.strength), float(item.confidence)),
            )

            if not best_evidence.quote:
                score = min(score, 0.5)
                group_confidence = min(group_confidence, 0.3)

            if group not in focus_groups and score > 1.0:
                score = min(score, 1.0)
                group_confidence = min(group_confidence, 0.65)

            if len(answer_text.strip().split()) < 8:
                score = min(score, 0.5)
                group_confidence = min(group_confidence, 0.35)

            guarded_scores[group] = round(self._clamp(score, 0, 2), 4)
            guarded_confidence[group] = round(
                self._clamp(group_confidence, 0, 1),
                4,
            )

        guarded_evidence = [
            RiasecEvidence(
                group=item.group,
                quote=item.quote,
                strength=min(float(item.strength), guarded_scores.get(item.group, 0)),
                confidence=min(
                    float(item.confidence),
                    guarded_confidence.get(item.group, 0),
                ),
            )
            for item in evidence
            if guarded_scores.get(item.group, 0) > 0
        ]

        return guarded_scores, guarded_confidence, guarded_evidence

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
