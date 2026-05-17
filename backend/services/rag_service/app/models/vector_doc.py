from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from .base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_document_chunks_content_hash"),
        {"schema": settings.DB_SCHEMA},
    )

    id = Column(Integer, primary_key=True)
    source_path = Column(String(500), nullable=False, index=True)
    source_name = Column(String(255), nullable=False, index=True)
    region = Column(String(100), nullable=True, index=True)
    university_name = Column(String(255), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    chunk_metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
