from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.session import (
    StartSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.profile_client import get_current_student_id
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["RIASEC Sessions"])


@router.post("", response_model=StartSessionResponse)
async def start_session(
    student_id: UUID = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return await service.start_session(student_id)


@router.post("/{session_id}/answers", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: UUID,
    payload: SubmitAnswerRequest,
    student_id: UUID = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return await service.submit_answer(
        session_id=session_id,
        answer_text=payload.answer_text,
        student_id=student_id,
    )
