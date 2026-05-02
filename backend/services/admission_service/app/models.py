from sqlalchemy import Column, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), nullable=False)
    input_features = Column(JSON, nullable=False) # Lưu tổ hợp môn và điểm
    predicted_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)