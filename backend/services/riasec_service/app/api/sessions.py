from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.session import (
    StartSessionRequest,
    StartSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    RiasecSessionResponse,
)
from app.services.profile_client import ensure_student_exists
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["RIASEC Sessions"])


@router.post("", response_model=StartSessionResponse)
async def start_session(
    payload: StartSessionRequest,
    db: Session = Depends(get_db),
):
    await ensure_student_exists(payload.student_id)

    service = SessionService(db)
    return await service.start_session(payload.student_id)


@router.get("/{session_id}", response_model=RiasecSessionResponse)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return service.get_session_or_404(session_id)


@router.post("/{session_id}/answers", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: UUID,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return await service.submit_answer(
        session_id=session_id,
        answer_text=payload.answer_text,
    )


@router.patch("/{session_id}/abandon", response_model=RiasecSessionResponse)
def abandon_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return service.abandon_session(session_id)
