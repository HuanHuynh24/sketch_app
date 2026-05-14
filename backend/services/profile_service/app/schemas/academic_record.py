from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AcademicRecordUpsertRequest(BaseModel):
    grade_10_avg: Optional[float] = None
    grade_11_avg: Optional[float] = None
    grade_12_avg: Optional[float] = None
    exam_scores: Dict[str, float]
    exam_type: str
    exam_year: int


class AcademicRecordResponse(BaseModel):
    record_id: UUID
    student_id: UUID
    grade_10_avg: Optional[float]
    grade_11_avg: Optional[float]
    grade_12_avg: Optional[float]
    exam_scores: Dict[str, float]
    exam_type: str
    exam_year: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)