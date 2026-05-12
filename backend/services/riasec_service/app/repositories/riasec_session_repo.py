from sqlalchemy.orm import Session
from app.models.riasec_session import RiasecSession
from datetime import datetime

class RiasecSessionRepository:
    def get_by_id(self, db: Session, session_id: str) -> RiasecSession | None:
        return db.query(RiasecSession).filter(RiasecSession.session_id == session_id).first()

    def get_active_session_by_student_id(self, db: Session, student_id: str) -> RiasecSession | None:
        return (
            db.query(RiasecSession)
            .filter(
                RiasecSession.student_id == student_id,
                RiasecSession.status == "in_progress",
            )
            .first()
        )

    def create(self, db: Session, student_id: str) -> RiasecSession:
        new_session = RiasecSession(student_id=student_id, question_count=1)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    def update_session(
        self, db: Session, session: RiasecSession, current_scores: dict, groups_asked: dict, confidence: float, question_count: int = None
    ) -> RiasecSession:
        session.current_scores = current_scores.copy()
        session.groups_asked = groups_asked.copy()
        session.confidence = confidence
        if question_count is not None:
            session.question_count = question_count
        db.commit()
        db.refresh(session)
        return session

    def complete_session(self, db: Session, session: RiasecSession) -> RiasecSession:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    def abandon_session(self, db: Session, session: RiasecSession) -> RiasecSession:
        session.status = "abandoned"
        db.commit()
        db.refresh(session)
        return session

riasec_session_repo = RiasecSessionRepository()
