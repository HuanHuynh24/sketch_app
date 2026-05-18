from uuid import UUID

from sqlalchemy.orm import Session

from app.models.university_recommendation import UniversityRecommendation
from app.repositories.recommendation_repository import UniversityRecommendationRepository
from app.schemas.recommendation import UniversityRecommendationCreate


class UniversityRecommendationService:
    def __init__(self, db: Session):
        self.recommendation_repo = UniversityRecommendationRepository(db)

    def list_by_student_id(
        self,
        student_id: UUID,
    ) -> list[UniversityRecommendation]:
        return self.recommendation_repo.list_by_student_id(student_id)

    def replace_for_student(
        self,
        student_id: UUID,
        recommendations: list[UniversityRecommendationCreate],
    ) -> list[UniversityRecommendation]:
        return self.recommendation_repo.replace_for_student(
            student_id=student_id,
            recommendations=recommendations,
        )
