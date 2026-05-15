from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DigitalCompetencyProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dcp_id: UUID
    student_id: UUID
    session_id: UUID
    riasec_code: str
    scores: dict
    confidence: dict
    career_groups: list
    digital_competencies: dict
    recommended_majors: list
    summary: str
    created_at: datetime
