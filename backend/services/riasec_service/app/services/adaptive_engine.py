import math

from app.core.config import settings
from app.core.constants import RIASEC_GROUPS


DEFAULT_FOCUS_GROUPS = ["R", "I"]
FOCUS_GROUP_POOL_SIZE = 4


class AdaptiveEngine:
    def build_riasec_code(self, scores: dict, top_n: int = 3) -> str:
        return "".join([item[0] for item in self._sort_scores(scores)[:top_n]])

    def calculate_entropy(self, scores: dict) -> float:
        total = sum(float(value) for value in scores.values())

        if total <= 0:
            return 1.0

        entropy = 0.0

        for group in RIASEC_GROUPS:
            p = float(scores.get(group, 0)) / total

            if p > 0:
                entropy -= p * math.log(p)

        max_entropy = math.log(len(RIASEC_GROUPS))

        return round(entropy / max_entropy, 4)

    def find_focus_groups(
        self,
        scores: dict,
        confidence: dict | None = None,
        asked_focus_groups: list[list[str]] | None = None,
    ) -> list[str]:
        confidence = confidence or {}
        asked_focus_groups = asked_focus_groups or []

        top_groups = self._sort_scores(scores)[:FOCUS_GROUP_POOL_SIZE]
        candidate_pairs = []

        for i in range(len(top_groups)):
            for j in range(i + 1, len(top_groups)):
                g1, s1 = top_groups[i]
                g2, s2 = top_groups[j]

                score_gap = abs(float(s1) - float(s2))
                avg_score = self._average(float(s1), float(s2))

                c1 = float(confidence.get(g1, 0))
                c2 = float(confidence.get(g2, 0))
                avg_confidence = self._average(c1, c2)

                priority = 0.0
                priority += max(0, 10 - score_gap)
                priority += avg_score
                priority += max(0, 1 - avg_confidence) * 5

                pair = sorted([g1, g2])

                if pair in asked_focus_groups:
                    priority -= 4

                candidate_pairs.append(
                    {
                        "pair": pair,
                        "priority": priority,
                    }
                )

        candidate_pairs = sorted(
            candidate_pairs,
            key=lambda item: item["priority"],
            reverse=True,
        )

        if candidate_pairs:
            return candidate_pairs[0]["pair"]

        return DEFAULT_FOCUS_GROUPS

    def should_terminate(
        self,
        current_step: int,
        scores: dict,
        confidence: dict,
    ) -> tuple[bool, str | None]:
        if current_step < settings.MIN_RIASEC_STEPS:
            return False, None

        if current_step >= settings.MAX_RIASEC_STEPS:
            return True, "Reached maximum number of questions"

        sorted_scores = self._sort_scores(scores)

        top_1 = sorted_scores[0]
        top_2 = sorted_scores[1]

        top_1_value = float(top_1[1])
        top_2_value = float(top_2[1])

        if top_1_value > 0:
            gap = (top_1_value - top_2_value) / top_1_value

            if gap >= settings.DOMINANT_GAP_THRESHOLD:
                return True, "Dominant RIASEC group gap reached threshold"

        top_3_groups = [item[0] for item in sorted_scores[:3]]

        avg_confidence = sum(
            float(confidence.get(group, 0))
            for group in top_3_groups
        ) / 3

        if avg_confidence >= settings.CONFIDENCE_THRESHOLD:
            return True, "Confidence threshold reached"

        return False, None

    def _sort_scores(self, scores: dict) -> list[tuple[str, float]]:
        return sorted(
            ((group, float(value)) for group, value in scores.items()),
            key=lambda item: item[1],
            reverse=True,
        )

    def _average(self, *values: float) -> float:
        return sum(values) / len(values)
