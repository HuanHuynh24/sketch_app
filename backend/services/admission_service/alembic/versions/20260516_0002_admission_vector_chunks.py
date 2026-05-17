"""admission_vector_chunks

Revision ID: 20260516_0002
Revises: 20260516_0001
Create Date: 2026-05-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260516_0002"
down_revision: Union[str, Sequence[str], None] = "20260516_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admission_document_chunks",
        sa.Column("chunk_id", sa.UUID(), nullable=False),
        sa.Column("raw_document_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("university_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_hash", sa.String(length=64), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("char_count", sa.Integer(), nullable=False),
        sa.Column("embedding_model", sa.String(length=80), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["raw_document_id"],
            ["admission.admission_raw_documents.raw_document_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["admission.admission_sources.source_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["admission.universities.university_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("chunk_id"),
        sa.UniqueConstraint(
            "raw_document_id",
            "chunk_index",
            name="uq_admission_document_chunks_raw_index",
        ),
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_document_chunks_raw_document_id"),
        "admission_document_chunks",
        ["raw_document_id"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_document_chunks_source_id"),
        "admission_document_chunks",
        ["source_id"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_document_chunks_university_id"),
        "admission_document_chunks",
        ["university_id"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_document_chunks_chunk_hash"),
        "admission_document_chunks",
        ["chunk_hash"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_document_chunks_embedding_model"),
        "admission_document_chunks",
        ["embedding_model"],
        unique=False,
        schema="admission",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_admission_admission_document_chunks_embedding_model"),
        table_name="admission_document_chunks",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_document_chunks_chunk_hash"),
        table_name="admission_document_chunks",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_document_chunks_university_id"),
        table_name="admission_document_chunks",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_document_chunks_source_id"),
        table_name="admission_document_chunks",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_document_chunks_raw_document_id"),
        table_name="admission_document_chunks",
        schema="admission",
    )
    op.drop_table("admission_document_chunks", schema="admission")
