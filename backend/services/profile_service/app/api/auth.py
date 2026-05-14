from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_student
from app.schemas.auth import AuthResponse, LoginRequest
from app.schemas.student import StudentRegisterRequest, StudentResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth")


@router.post("/register", response_model=AuthResponse)
def register(
    payload: StudentRegisterRequest,
    db: Session = Depends(get_db),
):
    return AuthService(db).register(payload)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    return AuthService(db).login(payload)


@router.get("/me", response_model=StudentResponse)
def get_me(
    current_student=Depends(get_current_student),
):
    return current_student