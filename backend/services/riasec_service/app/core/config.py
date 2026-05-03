import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Microservice"
    # Lấy DATABASE_URL từ file .env, nếu không có thì dùng chuỗi mặc định (để tránh lỗi)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:supersecretpassword@localhost:5432/admission_db"
    )

settings = Settings()