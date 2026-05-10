import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import Base

class UniversitiesMajors(Base):
    __tablename__ = "universities_majors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(String(200), nullable=False, index=True)
    logo = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Integer, nullable=False, default=0)
    name_universities = Column(String(20), nullable=False)
    name_majors = Column(String(200), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
