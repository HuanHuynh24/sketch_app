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

    # Các môn bắt buộc
    score_math = Column(Float, nullable=True)
    score_literature = Column(Float, nullable=True)

    # 2 môn tự chọn
    optional_subject_1 = Column(String(50), nullable=True)
    score_optional_1 = Column(Float, nullable=True)
    
    optional_subject_2 = Column(String(50), nullable=True)
    score_optional_2 = Column(Float, nullable=True)

    # Chứng chỉ tiếng Anh
    ielts_score = Column(Float, nullable=True)
    toeic_score = Column(Integer, nullable=True)
    
    exam_year = Column(Integer, nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student = relationship("Student")