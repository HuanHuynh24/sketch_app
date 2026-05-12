import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_student_id(self, db: Session, student_id: str):
        """Lấy thông tin User theo student_id (UUID), hỗ trợ an toàn ép kiểu từ string."""
        try:
            student_uuid = uuid.UUID(student_id) if isinstance(student_id, str) else student_id
        except (ValueError, AttributeError):
            return None
        return db.query(User).filter(User.student_id == student_uuid).first()

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

    def update_riasec_scores(self, db: Session, student_id: str, scores_100: dict, confidence: float, top_groups: list, riasec_code: str):
        user = self.get_by_student_id(db, student_id)
        if not user:
            return None
        user.score_R = scores_100.get("R", 0.0)
        user.score_I = scores_100.get("I", 0.0)
        user.score_A = scores_100.get("A", 0.0)
        user.score_S = scores_100.get("S", 0.0)
        user.score_E = scores_100.get("E", 0.0)
        user.score_C = scores_100.get("C", 0.0)
        user.riasec_code = riasec_code
        user.top_groups = top_groups
        user.confidence = confidence
        db.commit()
        db.refresh(user)
        return user

    def update_riasec_final(self, db: Session, student_id: str, final_data: dict):
        user = self.get_by_student_id(db, student_id)
        if not user:
            return None
        scores = final_data.get("scores", {})
        top_groups = final_data.get("top_groups", [])
        
        user.score_R = scores.get("R", 0.0)
        user.score_I = scores.get("I", 0.0)
        user.score_A = scores.get("A", 0.0)
        user.score_S = scores.get("S", 0.0)
        user.score_E = scores.get("E", 0.0)
        user.score_C = scores.get("C", 0.0)
        user.riasec_code = final_data.get("riasec_code")
        user.top_groups = top_groups
        user.confidence = final_data.get("confidence", 0.0)
        user.reasoning = final_data.get("reasoning")
        user.description = final_data.get("description")
        user.suggested_majors = final_data.get("suggested_majors")
        db.commit()
        db.refresh(user)
        return user

# Tạo một instance (Singleton) để gọi ở Service
user_repo = UserRepository()