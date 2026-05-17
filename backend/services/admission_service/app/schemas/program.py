from pydantic import BaseModel, Field
from typing import List, Optional

class ProgramSearchRequest(BaseModel):
    countries: List[str] = Field(default_factory=list)
    majors: List[str] = Field(default_factory=list)
    max_tuition: Optional[float] = None
    min_ielts: Optional[float] = None

class ProgramCreate(BaseModel):
    university_name: str
    country: str
    city: Optional[str] = None
    major_name: str
    degree_level: Optional[str] = None
    tuition_fee: Optional[float] = None
    currency: Optional[str] = "USD"
    ielts_requirement: Optional[float] = None
    source_url: Optional[str] = None

class ProgramResponse(BaseModel):
    id: int
    university_name: str
    country: str
    city: Optional[str] = None
    major_name: str
    degree_level: Optional[str] = None
    tuition_fee: Optional[float] = None
    currency: Optional[str] = None
    ielts_requirement: Optional[float] = None
    
    # Cho phép Pydantic đọc data từ SQLAlchemy object (orm_mode cũ trong v1)
    model_config = {"from_attributes": True}
