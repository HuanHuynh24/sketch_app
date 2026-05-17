"""pgvector_embeddings

Revision ID: 20260516_0003
Revises: 20260516_0002
Create Date: 2026-05-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "20260516_0003"
down_revision: Union[str, Sequence[str], None] = "20260516_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EMBEDDING_DIMENSION = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        "admission_document_chunks",
        sa.Column("embedding_provider", sa.String(length=30), nullable=True),
        schema="admission",
    )
    op.add_column(
        "admission_document_chunks",
        sa.Column(
            "embedding_vector",
            Vector(EMBEDDING_DIMENSION),
            nullable=True,
        ),
        schema="admission",
    )
    op.execute(
        """
        UPDATE admission.admission_document_chunks
        SET embedding_provider = 'local'
        WHERE embedding_provider IS NULL
        """
    )
    op.alter_column(
        "admission_document_chunks",
        "embedding_provider",
        nullable=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_document_chunks_embedding_provider"),
        "admission_document_chunks",
        ["embedding_provider"],
        unique=False,
        schema="admission",
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_admission_document_chunks_embedding_vector_hnsw
        ON admission.admission_document_chunks
        USING hnsw (embedding_vector vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS admission.ix_admission_document_chunks_embedding_vector_hnsw
        """
    )
    op.drop_index(
        op.f("ix_admission_admission_document_chunks_embedding_provider"),
        table_name="admission_document_chunks",
        schema="admission",
    )
    op.drop_column(
        "admission_document_chunks",
        "embedding_vector",
        schema="admission",
    )
    op.drop_column(
        "admission_document_chunks",
        "embedding_provider",
        schema="admission",
    )
