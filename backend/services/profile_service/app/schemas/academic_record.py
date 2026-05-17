from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


from typing import Literal

OptionalSubject = Literal[
    "Ngoại ngữ", "Lịch sử", "Vật lý", "Hóa học", "Sinh học", 
    "Địa lý", "Giáo dục kinh tế và pháp luật", "Tin học", "Công nghệ"
]

class AcademicRecordUpsertRequest(BaseModel):
    # Môn bắt buộc
    score_math: float = Field(ge=0, le=10)
    score_literature: float = Field(ge=0, le=10)
    
    # Môn tự chọn
    optional_subject_1: OptionalSubject
    score_optional_1: float = Field(ge=0, le=10)
    
    optional_subject_2: OptionalSubject
    score_optional_2: float = Field(ge=0, le=10)
    
    exam_year: int = Field(ge=2000, le=2100)
    ielts_score: Optional[float] = Field(default=None, ge=0, le=9.0)
    toeic_score: Optional[int] = Field(default=None, ge=0, le=990)

    @field_validator("optional_subject_2")
    @classmethod
    def check_different_subjects(cls, v: str, info) -> str:
        if "optional_subject_1" in info.data and v == info.data["optional_subject_1"]:
            raise ValueError("Hai môn tự chọn không được trùng nhau")
        return v


class AcademicRecordResponse(BaseModel):
    record_id: UUID
    student_id: UUID
    score_math: Optional[float]
    score_literature: Optional[float]
    optional_subject_1: Optional[str]
    score_optional_1: Optional[float]
    optional_subject_2: Optional[str]
    score_optional_2: Optional[float]
    exam_year: int
    ielts_score: Optional[float]
    toeic_score: Optional[int]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
