import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key")
    JWT_ALGORITHM: str = "HS256"
    
    # URL của các Microservices (Dùng tên container trong Docker)
    ADMISSION_SERVICE_URL: str = os.getenv("ADMISSION_SERVICE_URL", "http://ms_admission_service:8000")
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://ms_profile_service:8000")
    RIASEC_SERVICE_URL: str = os.getenv("RIASEC_SERVICE_URL", "http://ms_riasec_service:8000")
    RAG_SERVICE_URL: str = os.getenv("RAG_SERVICE_URL", "http://ms_rag_service:8000")

settings = Settings()