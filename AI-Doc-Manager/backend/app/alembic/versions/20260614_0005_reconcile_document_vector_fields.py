"""reconcile document vector fields

Revision ID: 20260614_0005
Revises: 20260508_0004
Create Date: 2026-06-14 00:00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260614_0005"
down_revision: str | None = "20260508_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE documents "
        "ADD COLUMN IF NOT EXISTS vertex_index_id VARCHAR(255)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS vertex_index_id")
