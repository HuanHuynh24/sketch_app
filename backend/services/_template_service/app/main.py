from fastapi import FastAPI
from app.api import health
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Gắn các API Router vào ứng dụng
app.include_router(health.router, tags=["Health Check"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}