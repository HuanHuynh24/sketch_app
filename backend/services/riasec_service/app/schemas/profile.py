from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RadarAxis(BaseModel):
    group: str
    label: str
    score: float
    max_score: float
    normalized_score: float
    confidence: float
    description: str


class RadarChartResponse(BaseModel):
    type: str
    max_score: float
    axes: list[RadarAxis]


class DominantGroupResponse(BaseModel):
    group: str
    label: str
    score: float
    confidence: float
    description: str


class GroupAnalysisResponse(BaseModel):
    group: str
    name: str
    label: str
    score: float
    confidence: float
    level: str
    description: str
    career_groups: list[str]
    recommended_majors: list[str]
    suitable_roles: list[str]
    digital_competencies: list[str]


class CareerRecommendationsResponse(BaseModel):
    riasec_code: str
    career_groups: list[str]
    recommended_majors: list[str]
    suitable_roles: list[str]
    digital_competencies: dict


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
    radar_chart: RadarChartResponse | None = None
    dominant_groups: list[DominantGroupResponse] | None = None
    group_analysis: list[GroupAnalysisResponse] | None = None
    career_recommendations: CareerRecommendationsResponse | None = None
