from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, RiasecScoresUpdate, RiasecFinalUpdate
from pydantic import BaseModel
from app.services.user_service import user_service
from app.api.deps import get_current_user
from app.models.user import User

class LoginResponse(Token):
    user: UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    API Đăng ký tài khoản mới.
    """
    new_user = user_service.create_user(db=db, user_in=user_in)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email này đã được sử dụng."
        )
    return new_user

@router.post("/login", response_model=LoginResponse)
def login_for_access_token(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    API Đăng nhập nhận JSON Body để lấy Access Token.
    Thống nhất toàn bộ hệ thống sử dụng application/json.
    """
    # Xác thực thông tin người dùng
    user = user_service.authenticate_user(db, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai email hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Tạo JWT Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) if hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES') else timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email, "student_id": str(user.student_id)}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    """
    API Đăng xuất. 
    Với JWT, backend không cần làm gì nhiều ngoài việc yêu cầu client xóa token ở local storage.
    """
    return {"message": "Đăng xuất thành công. Vui lòng xóa token ở client."}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    API Lấy thông tin cá nhân của người dùng đang đăng nhập.
    Yêu cầu phải có Header Authorization: Bearer <token>
    """
    return current_user

# ---------------------------------------------------------------------------
# API NỘI BỘ (Internal Microservice Endpoints)
# ---------------------------------------------------------------------------

@router.patch("/internal/users/{student_id}/riasec-scores")
def update_user_riasec_scores(
    student_id: str,
    data: RiasecScoresUpdate,
    db: Session = Depends(get_db)
):
    """
    API nội bộ: RIASEC service gọi để cập nhật điểm tạm thời của học sinh THPT.
    """
    user = user_service.update_riasec_scores(
        db=db,
        student_id=student_id,
        scores_100=data.scores_100,
        confidence=data.confidence,
        top_groups=data.top_groups,
        riasec_code=data.riasec_code
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "Scores updated successfully via internal API"}

@router.patch("/internal/users/{student_id}/riasec-final")
def update_user_riasec_final(
    student_id: str,
    data: RiasecFinalUpdate,
    db: Session = Depends(get_db)
):
    """
    API nội bộ: RIASEC service gọi để cập nhật báo cáo và phân tích trắc nghiệm cuối cùng từ Gemini.
    """
    user = user_service.update_riasec_final(
        db=db,
        student_id=student_id,
        final_data=data.final_data
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "Final scoring completed via internal API"}

@router.get("/internal/users/{student_id}")
def get_user_internal(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    API nội bộ: Lấy thông tin RIASEC từ bảng users.
    """
    user = user_service.get_by_student_id(db, student_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "student_id": str(user.student_id),
        "score_R": user.score_R,
        "score_I": user.score_I,
        "score_A": user.score_A,
        "score_S": user.score_S,
        "score_E": user.score_E,
        "score_C": user.score_C,
        "riasec_code": user.riasec_code,
        "top_groups": user.top_groups,
        "confidence": user.confidence,
        "reasoning": user.reasoning,
        "suggested_majors": user.suggested_majors
    }