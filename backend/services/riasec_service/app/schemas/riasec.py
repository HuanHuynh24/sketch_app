from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------
class SessionCreate(BaseModel):
    student_id: str


class SessionResponse(BaseModel):
    session_id: str
    first_question: Optional[str] = None
    question_no: Optional[int] = None
    status: Optional[str] = None
    question_count: Optional[int] = None
    confidence: Optional[float] = None


# ---------------------------------------------------------------------------
# Message (gửi/nhận câu trả lời)
# ---------------------------------------------------------------------------
class MessageCreate(BaseModel):
    answer: str = Field(..., max_length=2000)


class MessageResponse(BaseModel):
    status: str
    next_question: Optional[str] = None
    question_no: Optional[int] = None
    confidence: Optional[float] = None
    scores: Optional[Dict[str, float]] = None  # Realtime scores cho frontend


# ---------------------------------------------------------------------------
# Abandon
# ---------------------------------------------------------------------------
class SessionAbandonResponse(BaseModel):
    session_id: str
    status: str


# ---------------------------------------------------------------------------
# History — xem lại lịch sử hội thoại
# ---------------------------------------------------------------------------
class MessageItem(BaseModel):
    role: str
    content: str
    sequence_no: int


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]
    question_count: int
    status: str


# ---------------------------------------------------------------------------
# Result — xem kết quả RIASEC cuối cùng
# ---------------------------------------------------------------------------
class ScoreDetail(BaseModel):
    R: float = 0.0
    I: float = 0.0
    A: float = 0.0
    S: float = 0.0
    E: float = 0.0
    C: float = 0.0


class SuggestedMajor(BaseModel):
    group: str
    majors: List[str]
    fit_reason: str


class ResultResponse(BaseModel):
    session_id: str
    status: str
    scores: Optional[ScoreDetail] = None
    riasec_code: Optional[str] = None
    top_groups: Optional[List[str]] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    suggested_majors: Optional[List[SuggestedMajor]] = None


# ---------------------------------------------------------------------------
# Schemas cho API đơn Unified Chat Flow (1-API Flow)
# ---------------------------------------------------------------------------
class UnifiedChatRequest(BaseModel):
    student_id: Optional[str] = None
    answer: Optional[str] = None



class UnifiedChatResponse(BaseModel):
    status: str            # "in_progress" | "completed"
    session_id: str
    question_no: int
    message: str           # Câu hỏi tiếp theo hoặc lời chúc hoàn thành
    confidence: float
    scores: Dict[str, float]

