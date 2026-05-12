import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RIASEC Service"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:secret@postgres_db:5432/sketch_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "chuoi-bao-mat-cua-ban-o-day")
    JWT_ALGORITHM: str = "HS256"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # URL nội bộ của Profile Service để đồng bộ dữ liệu qua API
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://ms_profile_service:8000")

    # Gemini model — dùng 2.0-flash cho nhanh và rẻ hơn
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Groq Model cho phân tích hội thoại siêu tốc
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Toggle auth: True = JWT thật, False = mock để test nhanh
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"

    # Giới hạn câu hỏi bản chuẩn
    MAX_QUESTIONS: int = 25
    MIN_QUESTIONS: int = 8
    CONFIDENCE_THRESHOLD: float = 0.80
    GAP_THRESHOLD: float = 15.0

    class Config:
        env_file = ".env"

settings = Settings()