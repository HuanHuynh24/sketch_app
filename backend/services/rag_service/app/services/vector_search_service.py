import asyncio
import hashlib
import logging
from typing import Iterable

from google import genai
from google.genai import types
from sqlalchemy import func, not_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.vector_doc import DocumentChunk


logger = logging.getLogger(__name__)

DOMESTIC_COUNTRIES = ("vietnam", "viet nam", "việt nam", "vn")


class VectorSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
        self.client = None

        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")

    async def embed_query(self, text: str) -> list[float]:
        embeddings = await self._embed_texts([text], task_type="RETRIEVAL_QUERY")
        return embeddings[0]

    async def search_similar_programs(
        self,
        query: str,
        limit: int = 10,
        country_scope: str | None = None,
    ) -> list[dict]:
        if not query.strip():
            return []

        query_embedding = await self.embed_query(query)

        distance = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
        db_query = self.db.query(DocumentChunk, distance)
        db_query = self._apply_country_scope(db_query, country_scope)
        rows = db_query.order_by(distance).limit(limit).all()

        results = []
        for chunk, score in rows:
            metadata = dict(chunk.chunk_metadata or {})
            metadata.update(
                {
                    "source_path": chunk.source_path,
                    "source_name": chunk.source_name,
                    "region": chunk.region,
                    "university_name": chunk.university_name,
                    "chunk_index": chunk.chunk_index,
                }
            )
            results.append(
                {
                    "id": f"chunk_{chunk.id}",
                    "content": chunk.content,
                    "metadata": metadata,
                    "score": float(score) if score is not None else None,
                    "university_name": chunk.university_name or chunk.source_name,
                    "source_url": metadata.get("source_url") or metadata.get("source_path"),
                    "country": metadata.get("country") or "Vietnam",
                    "city": metadata.get("city") or metadata.get("region"),
                    "major_name": metadata.get("major_name") or metadata.get("matched_major"),
                }
            )

        return results

    def _apply_country_scope(self, db_query, country_scope: str | None):
        if not country_scope:
            return db_query

        country = func.lower(DocumentChunk.chunk_metadata["country"].astext)

        if country_scope == "domestic":
            return db_query.filter(country.in_(DOMESTIC_COUNTRIES))

        if country_scope == "foreign":
            return db_query.filter(
                DocumentChunk.chunk_metadata["country"].astext.isnot(None),
                not_(country.in_(DOMESTIC_COUNTRIES)),
            )

        raise ValueError(f"Unsupported country_scope: {country_scope}")

    async def save_chunk(self, content: str, meta: dict):
        content_hash = meta.get("content_hash")
        if not content_hash:
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        chunks = await self.save_chunks(
            [
                {
                    "content": content,
                    "source_path": meta.get("source_path") or meta.get("source_url") or "external",
                    "source_name": meta.get("source_name") or meta.get("source_url") or "external",
                    "region": meta.get("region"),
                    "university_name": meta.get("university_name"),
                    "chunk_index": int(meta.get("chunk_index") or 0),
                    "content_hash": content_hash,
                    "chunk_metadata": meta,
                }
            ]
        )
        return chunks[0] if chunks else None

    async def save_chunks(self, chunks: list[dict]) -> list[DocumentChunk]:
        if not chunks:
            return []

        prepared_chunks = [chunk for chunk in chunks if chunk.get("content", "").strip()]
        if not prepared_chunks:
            return []

        hashes = [chunk["content_hash"] for chunk in prepared_chunks if chunk.get("content_hash")]
        existing_hashes = set()
        if hashes:
            existing_hashes = {
                row[0]
                for row in self.db.query(DocumentChunk.content_hash)
                .filter(DocumentChunk.content_hash.in_(hashes))
                .all()
            }

        new_chunks = [
            chunk
            for chunk in prepared_chunks
            if chunk.get("content_hash") not in existing_hashes
        ]
        if not new_chunks:
            return []

        embeddings = await self._embed_in_batches(
            [chunk["content"] for chunk in new_chunks],
            batch_size=settings.RAG_EMBEDDING_BATCH_SIZE,
        )

        records = []
        for chunk, embedding in zip(new_chunks, embeddings):
            record = DocumentChunk(
                source_path=chunk["source_path"],
                source_name=chunk["source_name"],
                region=chunk.get("region"),
                university_name=chunk.get("university_name"),
                chunk_index=chunk["chunk_index"],
                content_hash=chunk["content_hash"],
                content=chunk["content"],
                embedding=embedding,
                chunk_metadata=chunk.get("chunk_metadata") or {},
            )
            self.db.add(record)
            records.append(record)

        self.db.commit()
        for record in records:
            self.db.refresh(record)

        logger.info("Saved %s new document chunks to pgvector", len(records))
        return records

    async def _embed_in_batches(self, texts: list[str], batch_size: int) -> list[list[float]]:
        embeddings = []
        for batch in self._batches(texts, batch_size):
            embeddings.extend(await self.embed_documents(batch))
        return embeddings

    async def _embed_texts(self, texts: list[str], task_type: str) -> list[list[float]]:
        if not self.client:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        return await asyncio.to_thread(self._embed_texts_sync, texts, task_type)

    def _embed_texts_sync(self, texts: list[str], task_type: str) -> list[list[float]]:
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(
                taskType=task_type,
                outputDimensionality=768,
            ),
        )
        raw_embeddings = getattr(response, "embeddings", None)
        if raw_embeddings is None:
            single_embedding = getattr(response, "embedding", None)
            raw_embeddings = [single_embedding] if single_embedding is not None else []

        embeddings = [self._embedding_values(item) for item in raw_embeddings]
        if len(embeddings) != len(texts):
            raise RuntimeError(
                f"Gemini returned {len(embeddings)} embeddings for {len(texts)} texts"
            )

        return embeddings

    def _embedding_values(self, embedding) -> list[float]:
        values = getattr(embedding, "values", None)
        if values is None and isinstance(embedding, dict):
            values = embedding.get("values")

        if not values:
            raise RuntimeError("Gemini embedding response did not include values")

        return [float(value) for value in values]

    def _batches(self, items: list[str], batch_size: int) -> Iterable[list[str]]:
        safe_batch_size = max(batch_size, 1)
        for index in range(0, len(items), safe_batch_size):
            yield items[index : index + safe_batch_size]
