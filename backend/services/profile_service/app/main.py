from fastapi import FastAPI
from app.api import health, users_router  # Nhớ import users_router
from app.core.config import settings

app = FastAPI(title=f"{settings.PROJECT_NAME} - Profile Service")

# Route kiểm tra sức khỏe
app.include_router(health.router, tags=["Health Check"])

# ĐÂY LÀ CHỖ CẦN KIỂM TRA KỸ NHẤT: prefix phải là /api/profile
app.include_router(users_router.router, prefix="/api/profile", tags=["Profile"])

@app.get("/")
def root():
    return {"message": f"Welcome to Profile Service of {settings.PROJECT_NAME}"}