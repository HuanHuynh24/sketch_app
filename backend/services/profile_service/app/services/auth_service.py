from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.student_repository import StudentRepository
from app.schemas.auth import AuthResponse, LoginRequest
from app.schemas.student import StudentRegisterRequest


ACCESS_TOKEN_EXPIRE_SECONDS = 3600


class AuthService:
    def __init__(self, db: Session):
        self.student_repo = StudentRepository(db)

    def register(self, payload: StudentRegisterRequest) -> AuthResponse:
        existing_student = self.student_repo.get_by_email(payload.email)

        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        student = self.student_repo.create(payload)

        access_token = create_access_token(
            subject=str(student.student_id),
            expires_seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
        )

        return AuthResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
            student=student,
        )

    def login(self, payload: LoginRequest) -> AuthResponse:
        student = self.student_repo.get_by_email(payload.email)

        if not student:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(payload.password, student.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not student.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        access_token = create_access_token(
            subject=str(student.student_id),
            expires_seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
        )

        return AuthResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
            student=student,
        )