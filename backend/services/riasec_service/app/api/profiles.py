from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import DigitalCompetencyProfileResponse
from app.services.profile_client import get_current_student_id

router = APIRouter(prefix="/profiles", tags=["Digital Competency Profiles"])


@router.get("/{dcp_id}", response_model=DigitalCompetencyProfileResponse)
def get_profile(
    dcp_id: UUID,
    student_id: UUID = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    repo = ProfileRepository(db)
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

    return profile
