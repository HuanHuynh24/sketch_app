import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.models.base import Base


class RiasecScoreSnapshot(Base):
    __tablename__ = "riasec_score_snapshots"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{settings.DB_SCHEMA}.riasec_sessions.session_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{settings.DB_SCHEMA}.conversation_messages.message_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
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

    dominant_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    decision_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    session = relationship(
        "RiasecSession",
        back_populates="snapshots",
    )