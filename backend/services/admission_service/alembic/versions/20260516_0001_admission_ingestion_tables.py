"""admission_ingestion_tables

Revision ID: 20260516_0001
Revises:
Create Date: 2026-05-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260516_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "universities",
        sa.Column("university_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("province", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=50), nullable=True),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("admission_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_year", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("university_id"),
        sa.UniqueConstraint("code", name="uq_admission_universities_code"),
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_universities_code"),
        "universities",
        ["code"],
        unique=False,
        schema="admission",
    )

    op.create_table(
        "admission_sources",
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("university_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["admission.universities.university_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("source_id"),
        sa.UniqueConstraint(
            "university_id",
            "url",
            "document_type",
            "year",
            name="uq_admission_sources_identity",
        ),
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_sources_university_id"),
        "admission_sources",
        ["university_id"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_sources_year"),
        "admission_sources",
        ["year"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_sources_status"),
        "admission_sources",
        ["status"],
        unique=False,
        schema="admission",
    )

    op.create_table(
        "admission_raw_documents",
        sa.Column("raw_document_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content_size", sa.Integer(), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["admission.admission_sources.source_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("raw_document_id"),
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_raw_documents_source_id"),
        "admission_raw_documents",
        ["source_id"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_admission_raw_documents_content_hash"),
        "admission_raw_documents",
        ["content_hash"],
        unique=False,
        schema="admission",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_admission_admission_raw_documents_content_hash"),
        table_name="admission_raw_documents",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_raw_documents_source_id"),
        table_name="admission_raw_documents",
        schema="admission",
    )
    op.drop_table("admission_raw_documents", schema="admission")
    op.drop_index(
        op.f("ix_admission_admission_sources_status"),
        table_name="admission_sources",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_sources_year"),
        table_name="admission_sources",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_admission_sources_university_id"),
        table_name="admission_sources",
        schema="admission",
    )
    op.drop_table("admission_sources", schema="admission")
    op.drop_index(
        op.f("ix_admission_universities_code"),
        table_name="universities",
        schema="admission",
    )
    op.drop_table("universities", schema="admission")
