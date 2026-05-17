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

    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "local-hashing-v1"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_TIMEOUT_SECONDS: float = 30.0

    OPENAI_API_KEY: str | None = None
    OPENAI_EMBEDDING_URL: str = "https://api.openai.com/v1/embeddings"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_CHAT_TIMEOUT_SECONDS: float = 25.0
    GEMINI_EMBEDDING_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_GENERATE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
