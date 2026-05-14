from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RIASEC Service"
    API_PREFIX: str = "/api/riasec"

    DATABASE_URL: str
    DB_SCHEMA: str = "riasec"

    PROFILE_SERVICE_URL: str = "http://profile_service:8000"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    MIN_RIASEC_STEPS: int = 5
    MAX_RIASEC_STEPS: int = 7
    DOMINANT_GAP_THRESHOLD: float = 0.2
    CONFIDENCE_THRESHOLD: float = 0.75

    class Config:
        env_file = ".env"


settings = Settings()