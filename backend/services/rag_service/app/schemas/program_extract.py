from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedProgram(BaseModel):
    university_name: str = Field(..., description="Tên trường Đại học bằng tiếng Anh")
    country: str = Field(..., description="Quốc gia của trường")
    city: Optional[str] = Field(..., description="Thành phố")
    major_name: str = Field(..., description="Tên chuyên ngành (ngành học) bằng tiếng Anh")
    degree_level: str = Field(..., description="Bậc học (Bachelor, Master, ...)")
    tuition_fee: Optional[float] = Field(..., description="Học phí mỗi năm (đổi ra USD). Nếu không có thì trả về null")
    currency: str = Field(..., description="Đơn vị tiền tệ của tuition_fee (bắt buộc quy đổi ra USD)")
    ielts_requirement: Optional[float] = Field(..., description="Yêu cầu IELTS tối thiểu. Ví dụ: 6.5. Nếu không có trả về null")

class ExtractionResult(BaseModel):
    programs: List[ExtractedProgram] = Field(..., description="Danh sách các chương trình học trích xuất được")
