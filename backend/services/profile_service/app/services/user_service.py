from sqlalchemy.orm import Session
from app.repositories.user_repo import user_repo
from app.schemas.user import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password

class UserService:
    def create_user(self, db: Session, user_in: UserCreate):
        existing_user = user_repo.get_by_email(db, email=user_in.email)
        if existing_user:
            return None 

        # Dùng hàm mã hóa xịn từ passlib
        hashed_pw = get_password_hash(user_in.password)
        return user_repo.create(db, user_in, hashed_password=hashed_pw)

    def authenticate_user(self, db: Session, user_login: UserLogin):
        user = user_repo.get_by_email(db, email=user_login.email)
        if not user:
            return None
        if not verify_password(user_login.password, user.password_hash):
            return None
        return user

    def update_riasec_scores(self, db: Session, student_id: str, scores_100: dict, confidence: float, top_groups: list, riasec_code: str):
        return user_repo.update_riasec_scores(
            db=db,
            student_id=student_id,
            scores_100=scores_100,
            confidence=confidence,
            top_groups=top_groups,
            riasec_code=riasec_code
        )

    def update_riasec_final(self, db: Session, student_id: str, final_data: dict):
        return user_repo.update_riasec_final(
            db=db,
            student_id=student_id,
            final_data=final_data
        )

    def get_by_student_id(self, db: Session, student_id: str):
        return user_repo.get_by_student_id(db, student_id)

user_service = UserService()