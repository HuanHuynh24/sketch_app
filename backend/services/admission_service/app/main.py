from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from .database import get_db, engine
from .models import Base, PredictionHistory

app = FastAPI(title="Admission Service API")

# Tự động tạo bảng prediction_history trong DB
Base.metadata.create_all(bind=engine)

class PredictionRequest(BaseModel):
    math_score: float
    physics_score: float
    chemistry_score: float

@app.post("/api/v1/admission/predict")
def predict_score(payload: PredictionRequest, request: Request, db: Session = Depends(get_db)):
    student_id_str = request.headers.get("X-User-Id")
    if not student_id_str:
        return {"error": "Unauthorized. Please go through API Gateway."}
        
    # --- MOCK LOGIC XGBOOST/LIGHTGBM ---
    # Chỗ này sau này bạn sẽ dùng joblib.load('model.pkl') để nạp model AI
    mock_prediction = round((payload.math_score + payload.physics_score + payload.chemistry_score) / 3 + 0.5, 2)
    
    # Lưu lịch sử dự đoán
    record = PredictionHistory(
        student_id=uuid.UUID(student_id_str),
        input_features=payload.model_dump(),
        predicted_score=mock_prediction
    )
    db.add(record)
    db.commit()
    
    return {
        "status": "success",
        "predicted_score": mock_prediction,
        "message": "Dự đoán bằng model XGBoost (Mock)"
    }