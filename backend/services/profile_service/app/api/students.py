from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.repositories.student_repository import StudentRepository
from app.schemas.student import StudentResponse, StudentUpdateRequest


router = APIRouter(prefix="/students")


@router.get("/me", response_model=StudentResponse)
def get_my_profile(
    current_student=Depends(get_current_student),
):
    return current_student


@router.patch("/me", response_model=StudentResponse)
def update_my_profile(
    payload: StudentUpdateRequest,
    current_student=Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return StudentRepository(db).update(current_student, payload)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_by_id(
    student_id: UUID,
    current_student=Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if student_id != current_student.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this student profile",
        )

    student = StudentRepository(db).get_by_id(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student
