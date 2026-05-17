"""add_university_recommendations

Revision ID: 8a4bb9f2f4a1
Revises: c53fda54fdde
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8a4bb9f2f4a1"
down_revision: Union[str, Sequence[str], None] = "c53fda54fdde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "university_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "logo",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("type", sa.Integer(), server_default="0", nullable=False),
        sa.Column("name_universities", sa.String(length=200), nullable=False),
        sa.Column("name_majors", sa.String(length=200), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "type IN (0, 1)",
            name="ck_university_recommendations_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_university_recommendations_student_id"),
        "university_recommendations",
        ["student_id"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        "ix_university_recommendations_student_updated_at",
        "university_recommendations",
        ["student_id", "updated_at"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        "ix_university_recommendations_content_gin",
        "university_recommendations",
        ["content"],
        unique=False,
        schema="admission",
        postgresql_using="gin",
    )
    op.create_index(
        op.f("ix_admission_university_recommendations_type"),
        "university_recommendations",
        ["type"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_university_recommendations_name_universities"),
        "university_recommendations",
        ["name_universities"],
        unique=False,
        schema="admission",
    )
    op.create_index(
        op.f("ix_admission_university_recommendations_name_majors"),
        "university_recommendations",
        ["name_majors"],
        unique=False,
        schema="admission",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_university_recommendations_content_gin",
        table_name="university_recommendations",
        schema="admission",
    )
    op.drop_index(
        "ix_university_recommendations_student_updated_at",
        table_name="university_recommendations",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_university_recommendations_name_majors"),
        table_name="university_recommendations",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_university_recommendations_name_universities"),
        table_name="university_recommendations",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_university_recommendations_type"),
        table_name="university_recommendations",
        schema="admission",
    )
    op.drop_index(
        op.f("ix_admission_university_recommendations_student_id"),
        table_name="university_recommendations",
        schema="admission",
    )
    op.drop_table("university_recommendations", schema="admission")
