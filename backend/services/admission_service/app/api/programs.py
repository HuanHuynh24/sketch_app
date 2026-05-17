from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.program import ProgramSearchRequest, ProgramResponse, ProgramCreate
from app.services.program_service import ProgramService

router = APIRouter(prefix="/programs", tags=["University Programs"])

@router.post("/search", response_model=List[ProgramResponse])
def search_programs(
    payload: ProgramSearchRequest,
    db: Session = Depends(get_db)
):
    """
    API nội bộ nhận request từ RAG Service (Layer 1 Search).
    """
    service = ProgramService(db)
    results = service.search_programs(payload)
    return results

@router.post("/bulk", response_model=List[ProgramResponse])
def create_programs(
    payload: List[ProgramCreate],
    db: Session = Depends(get_db)
):
    """
    API nội bộ nhận request từ RAG Service để lưu data vừa crawl.
    """
    service = ProgramService(db)
    results = service.bulk_create_programs(payload)
    return results
