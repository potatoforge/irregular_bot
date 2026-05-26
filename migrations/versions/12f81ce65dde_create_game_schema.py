"""create game schema

Revision ID: 12f81ce65dde
Revises: d281bad4966c
Create Date: 2026-05-26 10:37:34.777737

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "12f81ce65dde"
down_revision: Union[str, Sequence[str], None] = "d281bad4966c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS game")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
