from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, user_in: UserCreate, hashed_password: str):
        db_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            password_hash=hashed_password,
            province=getattr(user_in, 'province', 'Chưa cập nhật'),
            area_code=getattr(user_in, 'area_code', 'KV3'),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

# Tạo một instance (Singleton) để gọi ở Service
user_repo = UserRepository()