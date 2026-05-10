import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime
from app.models.base import Base

class RiasecSession(Base):
    __tablename__ = "riasec_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(String, index=True, nullable=False)
    status = Column(String(20), nullable=False, default="in_progress")
    question_count = Column(Integer, default=0)
    current_scores = Column(JSONB, default=lambda: {})
    confidence = Column(Float, default=0.0)
    groups_asked = Column(JSONB, default=lambda: {})
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
