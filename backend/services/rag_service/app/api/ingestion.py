from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.document_ingestion_service import DocumentIngestionService


router = APIRouter(prefix="/ingestion", tags=["RAG Ingestion"])


@router.post("/documents")
async def ingest_documents(db: Session = Depends(get_db)):
    return await DocumentIngestionService(db).ingest_markdown_directory()
