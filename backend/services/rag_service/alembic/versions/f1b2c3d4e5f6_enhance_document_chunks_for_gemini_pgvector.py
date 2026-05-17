"""enhance_document_chunks_for_gemini_pgvector

Revision ID: f1b2c3d4e5f6
Revises: 5c3cd6e7aafd
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "f1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "5c3cd6e7aafd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        ALTER TABLE rag.document_chunks
        ADD COLUMN IF NOT EXISTS source_path varchar(500),
        ADD COLUMN IF NOT EXISTS source_name varchar(255),
        ADD COLUMN IF NOT EXISTS region varchar(100),
        ADD COLUMN IF NOT EXISTS university_name varchar(255),
        ADD COLUMN IF NOT EXISTS chunk_index integer,
        ADD COLUMN IF NOT EXISTS content_hash varchar(64),
        ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now(),
        ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now()
        """
    )
    op.execute(
        """
        ALTER TABLE rag.document_chunks
        ALTER COLUMN chunk_metadata TYPE jsonb USING COALESCE(chunk_metadata::jsonb, '{}'::jsonb),
        ALTER COLUMN chunk_metadata SET DEFAULT '{}'::jsonb,
        ALTER COLUMN chunk_metadata SET NOT NULL
        """
    )
    op.execute(
        """
        UPDATE rag.document_chunks
        SET
            source_path = COALESCE(source_path, chunk_metadata->>'source_path', chunk_metadata->>'source_url', 'legacy'),
            source_name = COALESCE(source_name, chunk_metadata->>'source_name', chunk_metadata->>'source_url', 'legacy'),
            chunk_index = COALESCE(chunk_index, 0),
            content_hash = COALESCE(content_hash, md5(content))
        """
    )
    op.execute(
        """
        ALTER TABLE rag.document_chunks
        ALTER COLUMN source_path SET NOT NULL,
        ALTER COLUMN source_name SET NOT NULL,
        ALTER COLUMN chunk_index SET NOT NULL,
        ALTER COLUMN content_hash SET NOT NULL,
        ALTER COLUMN embedding SET NOT NULL
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_document_chunks_content_hash'
            ) THEN
                ALTER TABLE rag.document_chunks
                ADD CONSTRAINT uq_document_chunks_content_hash UNIQUE (content_hash);
            END IF;
        END $$;
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_content_hash ON rag.document_chunks (content_hash)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_region ON rag.document_chunks (region)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_source_name ON rag.document_chunks (source_name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_source_path ON rag.document_chunks (source_path)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_university_name ON rag.document_chunks (university_name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_metadata_gin ON rag.document_chunks USING gin (chunk_metadata)")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_rag_document_chunks_embedding_hnsw
        ON rag.document_chunks
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_metadata_gin")
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_university_name")
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_source_path")
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_source_name")
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_region")
    op.execute("DROP INDEX IF EXISTS rag.ix_rag_document_chunks_content_hash")
    op.execute("ALTER TABLE rag.document_chunks DROP CONSTRAINT IF EXISTS uq_document_chunks_content_hash")
    op.execute(
        """
        ALTER TABLE rag.document_chunks
        DROP COLUMN IF EXISTS updated_at,
        DROP COLUMN IF EXISTS created_at,
        DROP COLUMN IF EXISTS content_hash,
        DROP COLUMN IF EXISTS chunk_index,
        DROP COLUMN IF EXISTS university_name,
        DROP COLUMN IF EXISTS region,
        DROP COLUMN IF EXISTS source_name,
        DROP COLUMN IF EXISTS source_path
        """
    )
