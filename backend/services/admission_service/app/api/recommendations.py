from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recommendation import (
    UniversityRecommendationCreate,
    UniversityRecommendationResponse,
)
from app.services.recommendation_service import UniversityRecommendationService


router = APIRouter(prefix="/recommendations", tags=["University Recommendations"])


class RecommendationBulkReplaceRequest(BaseModel):
    student_id: UUID
    recommendations: List[UniversityRecommendationCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_same_student_id(self):
        for item in self.recommendations:
            if item.student_id != self.student_id:
                raise ValueError("All recommendations must belong to student_id")
        return self


@router.get(
    "/students/{student_id}",
    response_model=List[UniversityRecommendationResponse],
)
def list_recommendations(
    student_id: UUID,
    db: Session = Depends(get_db),
):
    return UniversityRecommendationService(db).list_by_student_id(student_id)


@router.post(
    "/bulk",
    response_model=List[UniversityRecommendationResponse],
)
def replace_recommendations(
    payload: RecommendationBulkReplaceRequest,
    db: Session = Depends(get_db),
):
    if not payload.recommendations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recommendations cannot be empty",
        )

    return UniversityRecommendationService(db).replace_for_student(
        student_id=payload.student_id,
        recommendations=payload.recommendations,
    )
