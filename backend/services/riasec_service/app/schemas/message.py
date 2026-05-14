from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message_id: UUID
    session_id: UUID
    role: str
    content: str
    message_type: str
    metadata_json: dict | None = None
    riasec_signal: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
