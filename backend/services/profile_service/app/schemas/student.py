from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class StudentRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    province: str
    area_code: str
    dob: Optional[date] = None
    priority_group: Optional[str] = None
    target_province: Optional[str] = None


class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None
    province: Optional[str] = None
    area_code: Optional[str] = None
    priority_group: Optional[str] = None
    target_province: Optional[str] = None


class StudentResponse(BaseModel):
    student_id: UUID
    full_name: str
    email: EmailStr
    dob: Optional[date]
    province: str
    area_code: str
    priority_group: Optional[str]
    target_province: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)