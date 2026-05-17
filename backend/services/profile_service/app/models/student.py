import uuid

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Date,
    DateTime,
    func,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, SchemaMixin


class Student(Base, SchemaMixin):
    __tablename__ = "students"

    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    dob = Column(Date, nullable=True)
    province = Column(String(100), nullable=False)
    area_code = Column(String(5), nullable=False)
    priority_group = Column(String(10), nullable=True)
    target_province = Column(String(100), nullable=True)
    target_country = Column(String(100), nullable=True)
    target_budget = Column(Integer, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )