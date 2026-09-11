"""create game schema

Revision ID: 12f81ce65dde
Revises: d281bad4966c
Create Date: 2026-05-26 10:37:34.777737

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "12f81ce65dde"
down_revision: str | Sequence[str] | None = "d281bad4966c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS game")


def downgrade() -> None:
    """Downgrade schema."""
