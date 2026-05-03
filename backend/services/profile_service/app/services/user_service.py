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
        if not verify_password(user_login.password, user.hashed_password):
            return None
        return user

user_service = UserService()