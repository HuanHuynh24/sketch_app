"""legacy_university_models_tombstone

Revision ID: c53fda54fdde
Revises:
Create Date: 2026-05-16 05:34:23.326805

This revision is intentionally empty.

Older development databases may already be stamped with this revision from the
removed university/program schema. Keeping the revision id lets Alembic upgrade
those databases to the current recommendation-only schema without resetting the
database.
"""
from typing import Sequence, Union


revision: str = "c53fda54fdde"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
