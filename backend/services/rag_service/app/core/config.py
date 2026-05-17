from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Microservice"
    API_PREFIX: str = "/api/service"

    DATABASE_URL: str = "postgresql://postgres:secret@postgres_db:5432/sketch_db"
    DB_SCHEMA: str = "public"

    JWT_SECRET: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"

    PROFILE_SERVICE_URL: str = "http://ms_profile_service:8000"
    RIASEC_SERVICE_URL: str = "http://ms_riasec_service:8000"
    ADMISSION_SERVICE_URL: str = "http://ms_admission_service:8000"
    RAG_SERVICE_URL: str = "http://ms_rag_service:8000"
    
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    RAG_DATA_DIR: str = "/data"
    RAG_AUTO_INGEST_ON_STARTUP: bool = False
    RAG_CHUNK_SIZE: int = 2800
    RAG_CHUNK_OVERLAP: int = 300
    RAG_EMBEDDING_BATCH_SIZE: int = 32

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
