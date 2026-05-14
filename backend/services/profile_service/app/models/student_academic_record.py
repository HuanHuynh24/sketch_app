import uuid

from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.models.base import Base, SchemaMixin


class StudentAcademicRecord(Base, SchemaMixin):
    __tablename__ = "student_academic_records"

    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.DB_SCHEMA}.students.student_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    grade_10_avg = Column(Float, nullable=True)
    grade_11_avg = Column(Float, nullable=True)
    grade_12_avg = Column(Float, nullable=True)

    exam_scores = Column(JSONB, nullable=False, default=dict)
    exam_type = Column(String(20), nullable=False)
    exam_year = Column(Integer, nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student = relationship("Student")