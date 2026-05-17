import logging

from fastapi import FastAPI

from app.api import health, ingestion, search
from app.core.config import settings
from app.core.database import SessionLocal, init_schema
from app.services.document_ingestion_service import DocumentIngestionService


logger = logging.getLogger(__name__)


app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
async def on_startup():
    init_schema()
    if settings.RAG_AUTO_INGEST_ON_STARTUP:
        db = SessionLocal()
        try:
            result = await DocumentIngestionService(db).ingest_markdown_directory()
            logger.info("RAG startup ingestion result: %s", result)
        except Exception as exc:
            logger.exception("RAG startup ingestion failed: %s", exc)
        finally:
            db.close()


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

app.include_router(
    ingestion.router,
    prefix=settings.API_PREFIX,
    tags=["RAG Ingestion"],
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
