from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import DEFAULT_CONFIDENCE, DEFAULT_SCORES
from app.models.riasec_session import RiasecSession


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, student_id: UUID) -> RiasecSession:
        session = RiasecSession(
            student_id=student_id,
            min_steps=settings.MIN_RIASEC_STEPS,
            max_steps=settings.MAX_RIASEC_STEPS,
            scores=DEFAULT_SCORES.copy(),
            confidence=DEFAULT_CONFIDENCE.copy(),
            current_focus_groups=[],
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_by_id(self, session_id: UUID) -> RiasecSession | None:
        return (
            self.db.query(RiasecSession)
            .filter(RiasecSession.session_id == session_id)
            .first()
        )

    def save(self, session: RiasecSession) -> RiasecSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session
