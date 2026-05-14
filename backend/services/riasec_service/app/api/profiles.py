from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import DigitalCompetencyProfileResponse

router = APIRouter(prefix="/profiles", tags=["Digital Competency Profiles"])


@router.get("/{dcp_id}", response_model=DigitalCompetencyProfileResponse)
def get_profile(
    dcp_id: UUID,
    db: Session = Depends(get_db),
):
    repo = ProfileRepository(db)
    profile = repo.get_by_id(dcp_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital competency profile not found",
        )

    return profile
