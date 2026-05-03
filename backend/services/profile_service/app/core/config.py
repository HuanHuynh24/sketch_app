import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sketch App - Profile Service"
    
    # Biến kết nối Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    DATABASE_URL: str

    # THÊM 2 DÒNG NÀY VÀO ĐÂY LÀ XONG
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-rat-la-bi-mat")
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()