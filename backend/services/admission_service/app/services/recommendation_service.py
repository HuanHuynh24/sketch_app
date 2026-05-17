from uuid import UUID

from sqlalchemy.orm import Session

from app.models.university_recommendation import UniversityRecommendation
from app.schemas.recommendation import UniversityRecommendationCreate


class UniversityRecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def list_by_student_id(
        self,
        student_id: UUID,
    ) -> list[UniversityRecommendation]:
        return (
            self.db.query(UniversityRecommendation)
            .filter(UniversityRecommendation.student_id == student_id)
            .order_by(UniversityRecommendation.updated_at.desc())
            .all()
        )

    def replace_for_student(
        self,
        student_id: UUID,
        recommendations: list[UniversityRecommendationCreate],
    ) -> list[UniversityRecommendation]:
        (
            self.db.query(UniversityRecommendation)
            .filter(UniversityRecommendation.student_id == student_id)
            .delete(synchronize_session=False)
        )

        created = [
            UniversityRecommendation(**item.model_dump())
            for item in recommendations
        ]

        self.db.add_all(created)
        self.db.commit()

        for item in created:
            self.db.refresh(item)

        return created
