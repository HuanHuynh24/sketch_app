import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.models.base import Base


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    message_id: Mapped[uuid.UUID] = mapped_column(
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

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    message_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="text",
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    riasec_signal: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    session = relationship(
        "RiasecSession",
        back_populates="messages",
    )