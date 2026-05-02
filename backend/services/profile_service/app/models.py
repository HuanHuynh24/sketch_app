from sqlalchemy import Column, String, Date, DateTime, Float, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from .database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False) # Họ và tên đầy đủ
    email = Column(String(200), unique=True, nullable=False) # Email đăng nhập[cite: 1]
    password_hash = Column(String(255), nullable=False) # Mật khẩu đã hash (bcrypt)[cite: 1]
    dob = Column(Date, nullable=True) # Ngày sinh[cite: 1]
    province = Column(String(100), nullable=False) # Tỉnh/thành phố hiện tại[cite: 1]
    area_code = Column(String(5), nullable=False) # Mã khu vực ưu tiên (KV1/KV2/KV3)[cite: 1]
    priority_group = Column(String(10), nullable=True) # Đối tượng ưu tiên (01–07)[cite: 1]
    target_province = Column(String(100), nullable=True) # Khu vực mong muốn học[cite: 1]
    created_at = Column(DateTime, default=func.now(), nullable=False) # Thời điểm đăng ký[cite: 1]