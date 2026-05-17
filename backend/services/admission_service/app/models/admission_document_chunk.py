import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.models.base import Base, SchemaMixin


class AdmissionDocumentChunk(Base, SchemaMixin):
    __tablename__ = "admission_document_chunks"
    __table_args__ = (
        UniqueConstraint(
            "raw_document_id",
            "chunk_index",
            name="uq_admission_document_chunks_raw_index",
        ),
        SchemaMixin.__table_args__,
    )

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    raw_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{settings.DB_SCHEMA}.admission_raw_documents.raw_document_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{settings.DB_SCHEMA}.admission_sources.source_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    university_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{settings.DB_SCHEMA}.universities.university_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(30), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSONB, nullable=False)
    embedding_vector: Mapped[list[float] | None] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=True,
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    raw_document = relationship("AdmissionRawDocument", back_populates="chunks")
    source = relationship("AdmissionSource")
    university = relationship("University")
