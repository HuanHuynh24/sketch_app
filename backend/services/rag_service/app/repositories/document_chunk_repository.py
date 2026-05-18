from sqlalchemy import func, not_, text
from sqlalchemy.orm import Session

from app.models.vector_doc import DocumentChunk


DOMESTIC_COUNTRIES = ("vietnam", "viet nam", "việt nam", "vn")


class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def has_chunks(self) -> bool:
        return self.db.query(DocumentChunk.id).first() is not None

    def get_source_metadata(self, source_path: str) -> list[tuple[str | None, str | None]]:
        return (
            self.db.query(
                DocumentChunk.chunk_metadata["file_hash"].astext,
                DocumentChunk.chunk_metadata["metadata_version"].astext,
            )
            .filter(DocumentChunk.source_path == source_path)
            .all()
        )

    def delete_by_source_path(self, source_path: str) -> None:
        (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.source_path == source_path)
            .delete(synchronize_session=False)
        )
        self.db.commit()

    def get_existing_hashes(self, content_hashes: list[str]) -> set[str]:
        if not content_hashes:
            return set()

        return {
            row[0]
            for row in self.db.query(DocumentChunk.content_hash)
            .filter(DocumentChunk.content_hash.in_(content_hashes))
            .all()
        }

    def create_many(self, chunks: list[dict]) -> list[DocumentChunk]:
        records = [
            DocumentChunk(
                source_path=chunk["source_path"],
                source_name=chunk["source_name"],
                region=chunk.get("region"),
                university_name=chunk.get("university_name"),
                chunk_index=chunk["chunk_index"],
                content_hash=chunk["content_hash"],
                content=chunk["content"],
                embedding=chunk["embedding"],
                chunk_metadata=chunk.get("chunk_metadata") or {},
            )
            for chunk in chunks
        ]

        self.db.add_all(records)
        self.db.commit()

        for record in records:
            self.db.refresh(record)

        return records

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int,
        country_scope: str | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        self._prefer_exact_filtered_search(country_scope)

        distance = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
        db_query = self.db.query(DocumentChunk, distance)
        db_query = self._apply_country_scope(db_query, country_scope)
        return db_query.order_by(distance).limit(limit).all()

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

    def _prefer_exact_filtered_search(self, country_scope: str | None) -> None:
        if not country_scope:
            return

        # With a selective WHERE filter, pgvector approximate indexes can return
        # too few candidates before PostgreSQL applies the country scope.
        # The current knowledge base is small enough that exact filtered scans
        # are both fast and much more predictable for domestic/foreign splits.
        self.db.execute(text("SET LOCAL enable_indexscan = off"))
        self.db.execute(text("SET LOCAL enable_bitmapscan = off"))
