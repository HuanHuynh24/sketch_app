import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.admission_document_chunk import AdmissionDocumentChunk
from app.models.admission_raw_document import AdmissionRawDocument
from app.models.admission_source import AdmissionSource
from app.models.university import University
from app.services.embedding_service import get_embedding_provider
from app.services.text_cleaner import clean_text


DEFAULT_CHUNK_SIZE = 1400
DEFAULT_CHUNK_OVERLAP = 180


@dataclass
class VectorIndexStats:
    documents_seen: int = 0
    documents_indexed: int = 0
    documents_skipped: int = 0
    chunks_created: int = 0
    chunks_deleted: int = 0


@dataclass
class VectorSearchResult:
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


def split_text(
    text: str,
    max_chars: int = DEFAULT_CHUNK_SIZE,
    overlap_chars: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    normalized = clean_text(text) or ""

    if not normalized:
        return []

    if len(normalized) <= max_chars:
        return [normalized]

    sentences = re.split(r"(?<=[.!?;:])\s+", normalized)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(sentence) > max_chars:
            chunks.extend(_split_long_text(sentence, max_chars, overlap_chars))
            current = ""
            continue

        next_chunk = f"{current} {sentence}".strip()

        if len(next_chunk) <= max_chars:
            current = next_chunk
            continue

        if current:
            chunks.append(current)
            current = _overlap_suffix(current, overlap_chars)

        current = f"{current} {sentence}".strip()

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]


def _split_long_text(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end].strip())

        if end == len(text):
            break

        start = max(0, end - overlap_chars)

    return chunks


def _overlap_suffix(text: str, overlap_chars: int) -> str:
    if overlap_chars <= 0 or len(text) <= overlap_chars:
        return ""

    return text[-overlap_chars:].strip()


def chunk_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def index_raw_document(
    db: Session,
    raw_document: AdmissionRawDocument,
    rebuild: bool = False,
) -> VectorIndexStats:
    stats = VectorIndexStats(documents_seen=1)
    provider = get_embedding_provider()

    existing_chunks = (
        db.query(AdmissionDocumentChunk)
        .filter(AdmissionDocumentChunk.raw_document_id == raw_document.raw_document_id)
    )
    existing_count = existing_chunks.count()
    matching_count = existing_chunks.filter(
        AdmissionDocumentChunk.embedding_provider == provider.provider_name,
        AdmissionDocumentChunk.embedding_model == provider.model_name,
        AdmissionDocumentChunk.embedding_dimension == provider.dimension,
        AdmissionDocumentChunk.embedding_vector.isnot(None),
    ).count()

    if matching_count and not rebuild:
        stats.documents_skipped = 1
        return stats

    if existing_count:
        stats.chunks_deleted = existing_count
        existing_chunks.delete(synchronize_session=False)

    if not raw_document.content_text:
        stats.documents_skipped = 1
        return stats

    source = raw_document.source
    university = source.university
    chunks = split_text(raw_document.content_text)

    if not chunks:
        stats.documents_skipped = 1
        return stats

    embeddings = []

    for batch in batched(chunks, max(1, settings.EMBEDDING_BATCH_SIZE)):
        embeddings.extend(provider.embed_many(batch, task="document"))

    if len(embeddings) != len(chunks):
        raise ValueError(
            f"Embedding provider returned {len(embeddings)} vectors for "
            f"{len(chunks)} chunks"
        )

    for index, (text, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            AdmissionDocumentChunk(
                raw_document_id=raw_document.raw_document_id,
                source_id=source.source_id,
                university_id=university.university_id,
                chunk_index=index,
                chunk_hash=chunk_hash(text),
                chunk_text=text,
                char_count=len(text),
                embedding_provider=embedding.provider,
                embedding_model=embedding.model,
                embedding_dimension=embedding.dimension,
                embedding=embedding.vector,
                embedding_vector=embedding.vector,
                metadata_json={
                    "source_url": source.url,
                    "final_url": raw_document.url,
                    "content_type": raw_document.content_type,
                    "source_title": source.title,
                },
            )
        )

    stats.documents_indexed = 1
    stats.chunks_created = len(chunks)
    return stats


def index_latest_documents(
    db: Session,
    rebuild: bool = False,
    university_code: str | None = None,
    limit: int | None = None,
) -> VectorIndexStats:
    query = (
        db.query(AdmissionSource)
        .options(
            joinedload(AdmissionSource.university),
            joinedload(AdmissionSource.raw_documents),
        )
        .filter(AdmissionSource.status == "fetched")
    )

    if university_code:
        query = query.join(University).filter(University.code == university_code)

    stats = VectorIndexStats()

    for source in query.all():
        latest = latest_raw_document(source.raw_documents)

        if latest is None:
            stats.documents_seen += 1
            stats.documents_skipped += 1
            continue

        document_stats = index_raw_document(db, latest, rebuild=rebuild)
        stats.documents_seen += document_stats.documents_seen
        stats.documents_indexed += document_stats.documents_indexed
        stats.documents_skipped += document_stats.documents_skipped
        stats.chunks_created += document_stats.chunks_created
        stats.chunks_deleted += document_stats.chunks_deleted

        if limit is not None and stats.documents_seen >= limit:
            break

    db.commit()
    return stats


def latest_raw_document(
    raw_documents: Iterable[AdmissionRawDocument],
) -> AdmissionRawDocument | None:
    documents = list(raw_documents)

    if not documents:
        return None

    return max(documents, key=lambda document: document.fetched_at)


def batched(items: list[str], batch_size: int) -> Iterable[list[str]]:
    for start in range(0, len(items), batch_size):
        yield items[start:start + batch_size]


def search_admission_chunks(
    db: Session,
    query_text: str,
    top_k: int = 5,
    province: str | None = None,
    university_code: str | None = None,
    year: int | None = None,
) -> list[VectorSearchResult]:
    provider = get_embedding_provider()
    query_embedding = provider.embed(query_text, task="query")
    distance = AdmissionDocumentChunk.embedding_vector.cosine_distance(
        query_embedding.vector,
    ).label("distance")

    query = (
        db.query(
            AdmissionDocumentChunk,
            University,
            AdmissionSource,
            distance,
        )
        .select_from(AdmissionDocumentChunk)
        .join(University, University.university_id == AdmissionDocumentChunk.university_id)
        .join(AdmissionSource, AdmissionSource.source_id == AdmissionDocumentChunk.source_id)
        .filter(
            AdmissionSource.status == "fetched",
            AdmissionDocumentChunk.embedding_provider == query_embedding.provider,
            AdmissionDocumentChunk.embedding_model == query_embedding.model,
            AdmissionDocumentChunk.embedding_dimension == query_embedding.dimension,
            AdmissionDocumentChunk.embedding_vector.isnot(None),
        )
    )

    if province:
        query = query.filter(University.province.ilike(f"%{province}%"))

    if university_code:
        query = query.filter(University.code == university_code)

    if year:
        query = query.filter(AdmissionSource.year == year)

    query = query.order_by(distance).limit(top_k)
    scored_results = []

    for chunk, university, source, vector_distance in query.all():
        score = 1.0 - float(vector_distance)
        scored_results.append(
            VectorSearchResult(
                chunk_id=str(chunk.chunk_id),
                score=round(score, 6),
                chunk_text=chunk.chunk_text,
                university_code=university.code,
                university_name=university.name,
                province=university.province,
                source_url=source.url,
                document_type=source.document_type,
                year=source.year,
                raw_document_id=str(chunk.raw_document_id),
                metadata=chunk.metadata_json,
            )
        )

    return scored_results


def get_vector_index_stats(db: Session) -> dict[str, object]:
    provider = get_embedding_provider()

    return {
        "chunks": db.query(AdmissionDocumentChunk).count(),
        "vector_chunks": (
            db.query(AdmissionDocumentChunk)
            .filter(AdmissionDocumentChunk.embedding_vector.isnot(None))
            .count()
        ),
        "indexed_documents": (
            db.query(AdmissionDocumentChunk.raw_document_id)
            .distinct()
            .count()
        ),
        "indexed_universities": (
            db.query(AdmissionDocumentChunk.university_id)
            .distinct()
            .count()
        ),
        "embedding_provider": provider.provider_name,
        "embedding_model": provider.model_name,
        "embedding_dimension": provider.dimension,
    }
