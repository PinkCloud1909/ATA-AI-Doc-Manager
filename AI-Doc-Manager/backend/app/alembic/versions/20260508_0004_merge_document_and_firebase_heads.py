"""merge document and firebase migration heads

Revision ID: 20260508_0004
Revises: 20260501_0003, 20260507_0003
Create Date: 2026-05-08 00:00:00
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "20260508_0004"
down_revision: tuple[str, str] = ("20260501_0003", "20260507_0003")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
