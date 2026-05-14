from fastapi import FastAPI

from app.api import health, profiles, sessions
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs",
)

app.include_router(health.router)
app.include_router(health.router, prefix=settings.API_PREFIX)

app.include_router(sessions.router, prefix=settings.API_PREFIX)
app.include_router(profiles.router, prefix=settings.API_PREFIX)
