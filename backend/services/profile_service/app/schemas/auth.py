from uuid import UUID

from pydantic import BaseModel, EmailStr
from app.schemas.student import StudentResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    student: StudentResponse