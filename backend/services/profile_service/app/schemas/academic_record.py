from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AcademicRecordUpsertRequest(BaseModel):
    grade_10_avg: Optional[float] = Field(default=None, ge=0, le=10)
    grade_11_avg: Optional[float] = Field(default=None, ge=0, le=10)
    grade_12_avg: Optional[float] = Field(default=None, ge=0, le=10)
    exam_scores: Dict[str, float] = Field(min_length=1)
    exam_type: str = Field(min_length=1, max_length=20)
    exam_year: int = Field(ge=2000, le=2100)

    @field_validator("exam_scores")
    @classmethod
    def validate_exam_scores(cls, value: Dict[str, float]) -> Dict[str, float]:
        for subject, score in value.items():
            if not subject.strip():
                raise ValueError("Exam score subject cannot be empty")

            if score < 0 or score > 10:
                raise ValueError("Exam scores must be between 0 and 10")

        return value


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
