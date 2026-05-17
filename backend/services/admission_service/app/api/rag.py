from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.rag_schema import (
    AdmissionChatRequest,
    AdmissionChatResponse,
    AdmissionChatSource,
    VectorIndexRequest,
    VectorIndexResponse,
    VectorSearchItem,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorStatsResponse,
)
from app.services.vector_index_service import (
    get_vector_index_stats,
    index_latest_documents,
    search_admission_chunks,
)
from app.services.admission_chat_service import answer_admission_question


router = APIRouter(prefix="/rag")


@router.get("/stats", response_model=VectorStatsResponse)
def vector_stats(db: Session = Depends(get_db)):
    return get_vector_index_stats(db)


@router.post("/index", response_model=VectorIndexResponse)
def build_vector_index(
    request: VectorIndexRequest,
    db: Session = Depends(get_db),
):
    return index_latest_documents(
        db=db,
        rebuild=request.rebuild,
        university_code=request.university_code,
        limit=request.limit,
    )


@router.post("/search", response_model=VectorSearchResponse)
def search_vectors(
    request: VectorSearchRequest,
    db: Session = Depends(get_db),
):
    results = search_admission_chunks(
        db=db,
        query_text=request.query,
        top_k=request.top_k,
        province=request.province,
        university_code=request.university_code,
        year=request.year,
    )

    return VectorSearchResponse(
        query=request.query,
        top_k=request.top_k,
        results=[
            VectorSearchItem(
                chunk_id=result.chunk_id,
                score=result.score,
                chunk_text=result.chunk_text,
                university_code=result.university_code,
                university_name=result.university_name,
                province=result.province,
                source_url=result.source_url,
                document_type=result.document_type,
                year=result.year,
                raw_document_id=result.raw_document_id,
                metadata=result.metadata,
            )
            for result in results
        ],
    )


@router.post("/chat", response_model=AdmissionChatResponse)
def chat_about_admission(
    request: AdmissionChatRequest,
    db: Session = Depends(get_db),
):
    answer = answer_admission_question(
        db=db,
        question=request.question,
        top_k=request.top_k,
        province=request.province,
        university_code=request.university_code,
        year=request.year,
        use_llm=request.use_llm,
    )

    return AdmissionChatResponse(
        question=answer.question,
        answer=answer.answer,
        used_llm=answer.used_llm,
        model=answer.model,
        sources=[
            AdmissionChatSource(
                citation_id=source.citation_id,
                chunk_id=source.result.chunk_id,
                score=source.result.score,
                university_code=source.result.university_code,
                university_name=source.result.university_name,
                province=source.result.province,
                source_url=source.result.source_url,
                document_type=source.result.document_type,
                year=source.result.year,
                snippet=source.snippet,
            )
            for source in answer.sources
        ],
    )
