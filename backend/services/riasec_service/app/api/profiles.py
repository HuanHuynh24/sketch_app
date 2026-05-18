from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import DigitalCompetencyProfileResponse
from app.services.profile_client import get_current_student_id
from app.services.report_service import ReportService

router = APIRouter(prefix="/profiles", tags=["Digital Competency Profiles"])


def build_profile_response(profile, report_service: ReportService) -> dict:
    return {
        "dcp_id": profile.dcp_id,
        "student_id": profile.student_id,
        "session_id": profile.session_id,
        "riasec_code": profile.riasec_code,
        "scores": profile.scores,
        "confidence": profile.confidence,
        "career_groups": profile.career_groups,
        "digital_competencies": profile.digital_competencies,
        "recommended_majors": profile.recommended_majors,
        "summary": profile.summary,
        "created_at": profile.created_at,
        **report_service.build_result_payload(
            scores=profile.scores,
            confidence=profile.confidence,
            riasec_code=profile.riasec_code,
        ),
    }


@router.get("/latest", response_model=DigitalCompetencyProfileResponse)
def get_latest_profile(
    student_id: UUID = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    repo = ProfileRepository(db)
    report_service = ReportService(enable_llm=False)
    profile = repo.get_latest_by_student_id(student_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital competency profile not found",
        )

    return build_profile_response(profile, report_service)


@router.get("/{dcp_id}", response_model=DigitalCompetencyProfileResponse)
def get_profile(
    dcp_id: UUID,
    student_id: UUID = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    repo = ProfileRepository(db)
    report_service = ReportService(enable_llm=False)
    profile = repo.get_by_id(dcp_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital competency profile not found",
        )

    if profile.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this RIASEC profile",
        )

    return build_profile_response(profile, report_service)
