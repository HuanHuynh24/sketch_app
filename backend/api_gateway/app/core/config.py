from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "API Gateway - Sketch App"

    JWT_SECRET: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"

    ADMISSION_SERVICE_URL: str = "http://ms_admission_service:8000"
    PROFILE_SERVICE_URL: str = "http://ms_profile_service:8000"
    RIASEC_SERVICE_URL: str = "http://ms_riasec_service:8000"
    RAG_SERVICE_URL: str = "http://ms_rag_service:8000"

    PROXY_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()