from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.student_academic_record import StudentAcademicRecord
from app.schemas.academic_record import AcademicRecordUpsertRequest


class AcademicRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_student_id(self, student_id: UUID) -> Optional[StudentAcademicRecord]:
        return (
            self.db.query(StudentAcademicRecord)
            .filter(StudentAcademicRecord.student_id == student_id)
            .first()
        )

    def create(
        self,
        student_id: UUID,
        data: AcademicRecordUpsertRequest,
    ) -> StudentAcademicRecord:
        record = StudentAcademicRecord(
            student_id=student_id,
            grade_10_avg=data.grade_10_avg,
            grade_11_avg=data.grade_11_avg,
            grade_12_avg=data.grade_12_avg,
            exam_scores=data.exam_scores,
            exam_type=data.exam_type,
            exam_year=data.exam_year,
        )

        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid academic record data",
            )

        self.db.refresh(record)

        return record

    def update(
        self,
        record: StudentAcademicRecord,
        data: AcademicRecordUpsertRequest,
    ) -> StudentAcademicRecord:
        record.grade_10_avg = data.grade_10_avg
        record.grade_11_avg = data.grade_11_avg
        record.grade_12_avg = data.grade_12_avg
        record.exam_scores = data.exam_scores
        record.exam_type = data.exam_type
        record.exam_year = data.exam_year

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid academic record data",
            )

        self.db.refresh(record)

        return record

    def upsert_by_student_id(
        self,
        student_id: UUID,
        data: AcademicRecordUpsertRequest,
    ) -> StudentAcademicRecord:
        record = self.get_by_student_id(student_id)

        if record:
            return self.update(record, data)

        return self.create(student_id, data)
