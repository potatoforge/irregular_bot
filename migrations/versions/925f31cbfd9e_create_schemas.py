"""create schemas

Revision ID: 925f31cbfd9e
Revises: 1c24fa128f0b
Create Date: 2026-05-23 12:55:50.619998

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "925f31cbfd9e"
down_revision: Union[str, Sequence[str], None] = "1c24fa128f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS tg")
    op.execute("CREATE SCHEMA IF NOT EXISTS eng")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
