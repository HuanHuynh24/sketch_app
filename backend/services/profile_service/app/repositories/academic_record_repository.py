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
            score_math=data.score_math,
            score_literature=data.score_literature,
            optional_subject_1=data.optional_subject_1,
            score_optional_1=data.score_optional_1,
            optional_subject_2=data.optional_subject_2,
            score_optional_2=data.score_optional_2,
            exam_year=data.exam_year,
            ielts_score=data.ielts_score,
            toeic_score=data.toeic_score,
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
        record.score_math = data.score_math
        record.score_literature = data.score_literature
        record.optional_subject_1 = data.optional_subject_1
        record.score_optional_1 = data.score_optional_1
        record.optional_subject_2 = data.optional_subject_2
        record.score_optional_2 = data.score_optional_2
        record.exam_year = data.exam_year
        record.ielts_score = data.ielts_score
        record.toeic_score = data.toeic_score

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
