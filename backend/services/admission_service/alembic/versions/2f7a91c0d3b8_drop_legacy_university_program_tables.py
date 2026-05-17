"""drop_legacy_university_program_tables

Revision ID: 2f7a91c0d3b8
Revises: 8a4bb9f2f4a1
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "2f7a91c0d3b8"
down_revision: Union[str, Sequence[str], None] = "8a4bb9f2f4a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS admission.university_programs CASCADE")
    op.execute("DROP TABLE IF EXISTS admission.universities CASCADE")


def downgrade() -> None:
    pass
