from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UniversityRecommendationCreate(BaseModel):
    student_id: UUID
    logo: list[str] = Field(default_factory=list)
    content: dict[str, Any]
    description: str = Field(min_length=1)
    type: int = Field(default=0, ge=0, le=1)
    name_universities: str = Field(min_length=1, max_length=200)
    name_majors: str = Field(min_length=1, max_length=200)


class UniversityRecommendationResponse(BaseModel):
    id: UUID
    student_id: UUID
    logo: list[str]
    content: dict[str, Any]
    description: str
    type: int
    name_universities: str
    name_majors: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
