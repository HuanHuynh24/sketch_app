from uuid import UUID

from sqlalchemy.orm import Session

from app.models.riasec_score_snapshot import RiasecScoreSnapshot


class ScoreSnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session_id: UUID,
        message_id: UUID | None,
        scores: dict,
        confidence: dict,
        entropy: float,
        dominant_code: str | None,
        decision_reason: str | None,
    ) -> RiasecScoreSnapshot:
        snapshot = RiasecScoreSnapshot(
            session_id=session_id,
            message_id=message_id,
            scores=scores,
            confidence=confidence,
            entropy=entropy,
            dominant_code=dominant_code,
            decision_reason=decision_reason,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot
