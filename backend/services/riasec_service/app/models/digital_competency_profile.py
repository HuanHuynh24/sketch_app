import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.models.base import Base


class DigitalCompetencyProfile(Base):
    __tablename__ = "digital_competency_profiles"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    dcp_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
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

    riasec_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
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

    career_groups: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    digital_competencies: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    recommended_majors: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )