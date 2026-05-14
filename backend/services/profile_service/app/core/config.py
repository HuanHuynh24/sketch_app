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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()