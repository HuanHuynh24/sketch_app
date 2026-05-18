from uuid import UUID

from sqlalchemy.orm import Session

from app.models.digital_competency_profile import DigitalCompetencyProfile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        student_id: UUID,
        session_id: UUID,
        riasec_code: str,
        scores: dict,
        confidence: dict,
        career_groups: list,
        digital_competencies: dict,
        recommended_majors: list,
        summary: str,
    ) -> DigitalCompetencyProfile:
        profile = DigitalCompetencyProfile(
            student_id=student_id,
            session_id=session_id,
            riasec_code=riasec_code,
            scores=scores,
            confidence=confidence,
            career_groups=career_groups,
            digital_competencies=digital_competencies,
            recommended_majors=recommended_majors,
            summary=summary,
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile

    def get_by_id(self, dcp_id: UUID) -> DigitalCompetencyProfile | None:
        return (
            self.db.query(DigitalCompetencyProfile)
            .filter(DigitalCompetencyProfile.dcp_id == dcp_id)
            .first()
        )

    def get_latest_by_student_id(
        self,
        student_id: UUID,
    ) -> DigitalCompetencyProfile | None:
        return (
            self.db.query(DigitalCompetencyProfile)
            .filter(DigitalCompetencyProfile.student_id == student_id)
            .order_by(DigitalCompetencyProfile.created_at.desc())
            .first()
        )
