from pydantic import BaseModel, Field


class VectorIndexRequest(BaseModel):
    rebuild: bool = False
    university_code: str | None = Field(default=None, max_length=20)
    limit: int | None = Field(default=None, ge=1, le=500)


class VectorIndexResponse(BaseModel):
    documents_seen: int
    documents_indexed: int
    documents_skipped: int
    chunks_created: int
    chunks_deleted: int


class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)
    province: str | None = Field(default=None, max_length=100)
    university_code: str | None = Field(default=None, max_length=20)
    year: int | None = Field(default=None, ge=2000, le=2100)


class VectorSearchItem(BaseModel):
    chunk_id: str
    score: float
    chunk_text: str
    university_code: str
    university_name: str
    province: str | None
    source_url: str
    document_type: str
    year: int | None
    raw_document_id: str
    metadata: dict | None


class VectorSearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[VectorSearchItem]


class AdmissionChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1200)
    top_k: int = Field(default=6, ge=1, le=12)
    province: str | None = Field(default=None, max_length=100)
    university_code: str | None = Field(default=None, max_length=20)
    year: int | None = Field(default=None, ge=2000, le=2100)
    use_llm: bool = True


class AdmissionChatSource(BaseModel):
    citation_id: int
    chunk_id: str
    score: float
    university_code: str
    university_name: str
    province: str | None
    source_url: str
    document_type: str
    year: int | None
    snippet: str


class AdmissionChatResponse(BaseModel):
    question: str
    answer: str
    used_llm: bool
    model: str | None
    sources: list[AdmissionChatSource]


class VectorStatsResponse(BaseModel):
    chunks: int
    vector_chunks: int
    indexed_documents: int
    indexed_universities: int
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
