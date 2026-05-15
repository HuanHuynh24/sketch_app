from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message import MessageResponse


class SubmitAnswerRequest(BaseModel):
    answer_text: str = Field(min_length=1, max_length=3000)


class RiasecSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    student_id: UUID
    status: str
    current_step: int
    min_steps: int
    max_steps: int
    scores: dict
    confidence: dict
    entropy: float
    current_focus_groups: list
    riasec_code: str | None = None
    termination_reason: str | None = None
    final_summary: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class StartSessionResponse(BaseModel):
    session: RiasecSessionResponse
    question: MessageResponse


class SubmitAnswerResponse(BaseModel):
    status: str
    session: RiasecSessionResponse
    user_message: MessageResponse
    assistant_message: MessageResponse | None = None
    dcp_id: UUID | None = None
