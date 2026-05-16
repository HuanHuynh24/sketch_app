from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator


class StudentRegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    province: str = Field(min_length=1, max_length=100)
    area_code: str = Field(min_length=1, max_length=5)
    dob: Optional[date] = None
    priority_group: Optional[str] = Field(default=None, max_length=10)
    target_province: Optional[str] = Field(default=None, max_length=100)


class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    dob: Optional[date] = None
    province: Optional[str] = Field(default=None, min_length=1, max_length=100)
    area_code: Optional[str] = Field(default=None, min_length=1, max_length=5)
    priority_group: Optional[str] = Field(default=None, max_length=10)
    target_province: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="before")
    @classmethod
    def reject_null_for_required_fields(cls, data):
        if not isinstance(data, dict):
            return data

        required_fields = {"full_name", "province", "area_code"}
        null_fields = sorted(
            field for field in required_fields
            if field in data and data[field] is None
        )

        if null_fields:
            fields = ", ".join(null_fields)
            raise ValueError(f"{fields} cannot be null")

        return data


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
