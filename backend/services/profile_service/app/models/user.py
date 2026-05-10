import uuid
from sqlalchemy import (
    Column, String, Boolean, Date, Float,
    Integer, Text, TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from app.models.base import Base


class User(Base):
    """Bảng users — gộp toàn bộ thông tin học sinh, học lực, DCP và kết quả RIASEC."""

    __tablename__ = "users"

    # ------------------------------------------------------------------
    # PK
    # ------------------------------------------------------------------
    student_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Khóa chính định danh học sinh",
    )

    # ------------------------------------------------------------------
    # Thông tin cá nhân (students)
    # ------------------------------------------------------------------
    full_name       = Column(String(100),  nullable=False,                comment="Họ và tên đầy đủ")
    email           = Column(String(200),  nullable=False, unique=True,   comment="Email đăng nhập")
    password_hash   = Column(String(255),  nullable=False,                comment="Mật khẩu đã hash (bcrypt)")
    dob             = Column(Date,         nullable=True,                 comment="Ngày sinh")
    province        = Column(String(100),  nullable=False,                comment="Tỉnh/thành phố hiện tại")
    area_code       = Column(String(5),    nullable=False,                comment="Mã khu vực ưu tiên (KV1/KV2/KV3)")
    priority_group  = Column(String(10),   nullable=True,                 comment="Đối tượng ưu tiên (01–07)")
    target_province = Column(String(100),  nullable=True,                 comment="Khu vực mong muốn học")
    is_active       = Column(Boolean,      default=True,                  comment="Tài khoản còn hoạt động không")

    # ------------------------------------------------------------------
    # Kết quả học tập (academic_records)
    # ------------------------------------------------------------------
    grade_10_avg = Column(Float,       nullable=True,  comment="Điểm TB lớp 10")
    grade_11_avg = Column(Float,       nullable=True,  comment="Điểm TB lớp 11")
    grade_12_avg = Column(Float,       nullable=True,  comment="Điểm TB lớp 12")
    exam_scores  = Column(JSONB,       nullable=True,  comment="Điểm thi theo môn: {toan, van, anh, ly, hoa, sinh...}")
    exam_type    = Column(String(20),  nullable=True,  comment="thpt | dgnl | dgtd")
    exam_year    = Column(Integer,     nullable=True,  comment="Năm thi")

    # ------------------------------------------------------------------
    # Kết quả RIASEC (dcp_results)
    # ------------------------------------------------------------------
    score_R          = Column(Float,        nullable=True, comment="Điểm Realistic (0–100)")
    score_I          = Column(Float,        nullable=True, comment="Điểm Investigative (0–100)")
    score_A          = Column(Float,        nullable=True, comment="Điểm Artistic (0–100)")
    score_S          = Column(Float,        nullable=True, comment="Điểm Social (0–100)")
    score_E          = Column(Float,        nullable=True, comment="Điểm Enterprising (0–100)")
    score_C          = Column(Float,        nullable=True, comment="Điểm Conventional (0–100)")
    riasec_code      = Column(String(3),    nullable=True, comment="Mã Holland nổi trội, ví dụ: RI, RIA")
    top_groups       = Column(ARRAY(String),nullable=True, comment="Mảng nhóm nổi trội: ['R','I']")
    confidence       = Column(Float,        nullable=True, comment="Độ tin cậy kết quả (0.0–1.0)")
    reasoning        = Column(Text,         nullable=True, comment="Lý giải AI dựa trên bằng chứng hội thoại")
    suggested_majors = Column(JSONB,        nullable=True, comment="Danh sách nhóm ngành gợi ý + mô tả")
    created_at   = Column(TIMESTAMP(timezone=True), nullable=True, comment="Thời điểm tạo user")
    updated_at   = Column(TIMESTAMP(timezone=True), nullable=True, comment="Thời điểm cập nhật user")   