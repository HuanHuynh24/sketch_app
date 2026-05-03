from fastapi import FastAPI
from app.api import health, predict_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health.router, tags=["Health Check"])
app.include_router(predict_router.router, prefix="/api/admission", tags=["Prediction"]) # <-- Gắn router vào đây