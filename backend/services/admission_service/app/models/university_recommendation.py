import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.config import settings
from app.models.base import Base, SchemaMixin


class UniversityRecommendation(Base, SchemaMixin):
    __tablename__ = "university_recommendations"
    __table_args__ = (
        CheckConstraint(
            "type IN (0, 1)",
            name="ck_university_recommendations_type",
        ),
        Index(
            "ix_university_recommendations_student_updated_at",
            "student_id",
            "updated_at",
        ),
        Index(
            "ix_university_recommendations_content_gin",
            "content",
            postgresql_using="gin",
        ),
        {"schema": settings.DB_SCHEMA},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    logo = Column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    content = Column(JSONB, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Integer, nullable=False, default=0, server_default="0", index=True)
    name_universities = Column(String(200), nullable=False, index=True)
    name_majors = Column(String(200), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
