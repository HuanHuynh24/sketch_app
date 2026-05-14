from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.repositories.academic_record_repository import AcademicRecordRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.academic_record import (
    AcademicRecordResponse,
    AcademicRecordUpsertRequest,
)


router = APIRouter(prefix="/students")


@router.get("/me/academic-record", response_model=AcademicRecordResponse)
def get_my_academic_record(
    current_student=Depends(get_current_student),
    db: Session = Depends(get_db),
):
    record = AcademicRecordRepository(db).get_by_student_id(
        current_student.student_id
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic record not found",
        )

    return record


@router.put("/me/academic-record", response_model=AcademicRecordResponse)
def upsert_my_academic_record(
    payload: AcademicRecordUpsertRequest,
    current_student=Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return AcademicRecordRepository(db).upsert_by_student_id(
        current_student.student_id,
        payload,
    )


@router.get("/{student_id}/academic-record", response_model=AcademicRecordResponse)
def get_student_academic_record(
    student_id: UUID,
    db: Session = Depends(get_db),
):
    student = StudentRepository(db).get_by_id(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    record = AcademicRecordRepository(db).get_by_student_id(student_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic record not found",
        )

    return record