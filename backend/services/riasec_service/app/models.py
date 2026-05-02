from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from .database import Base

class RiasecSession(Base):
    __tablename__ = "riasec_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # student_id liên kết "mềm" sang Profile Service
    student_id = Column(UUID(as_uuid=True), nullable=False) 
    status = Column(String(20), nullable=False, default="in_progress")
    question_count = Column(Integer, default=0)
    current_scores = Column(JSONB, default={})
    confidence = Column(Float, default=0.0)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("riasec_sessions.session_id"))
    role = Column(String(10), nullable=False) # 'user' hoặc 'assistant'
    content = Column(Text, nullable=False)
    sequence_no = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)