import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.models.base import Base


class RiasecSession(Base):
    __tablename__ = "riasec_sessions"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="in_progress",
        index=True,
    )

    current_step: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    min_steps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    max_steps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    confidence: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    entropy: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    current_focus_groups: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    riasec_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    termination_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    final_summary: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    messages = relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    snapshots = relationship(
        "RiasecScoreSnapshot",
        back_populates="session",
        cascade="all, delete-orphan",
    )