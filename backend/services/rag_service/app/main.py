from fastapi import FastAPI

from app.api import health, search
from app.core.config import settings
from app.core.database import init_schema


app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
def on_startup():
    init_schema()


app.include_router(
    health.router,
    prefix=settings.API_PREFIX,
    tags=["Health Check"],
)

app.include_router(
    search.router,
    prefix=settings.API_PREFIX,
    tags=["RAG Search"],
)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
    }


@app.get("/health")
def root_health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "schema": settings.DB_SCHEMA,
    }