from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentRegisterRequest, StudentUpdateRequest
from app.core.security import hash_password


class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, student_id: UUID) -> Optional[Student]:
        return (
            self.db.query(Student)
            .filter(Student.student_id == student_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[Student]:
        return (
            self.db.query(Student)
            .filter(Student.email == email)
            .first()
        )

    def create(self, data: StudentRegisterRequest) -> Student:
        student = Student(
            full_name=data.full_name,
            email=data.email,
            password_hash=hash_password(data.password),
            dob=data.dob,
            province=data.province,
            area_code=data.area_code,
            priority_group=data.priority_group,
            target_province=data.target_province,
        )

        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)

        return student

    def update(self, student: Student, data: StudentUpdateRequest) -> Student:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(student, field, value)

        self.db.commit()
        self.db.refresh(student)

        return student