"""document management fields

Revision ID: 20260501_0003
Revises: 20260423_0002
Create Date: 2026-05-01 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260501_0003"
down_revision: str | None = "20260423_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add document management metadata columns
    op.add_column(
        "documents",
        sa.Column("title", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("original_filename", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("file_size", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("content_type", sa.String(length=200), nullable=True),
    )
<<<<<<< HEAD
    op.add_column(
        "documents",
        sa.Column("vertex_index_id", sa.String(length=255), nullable=True),
    )

=======

    # Backfill title and original_filename for any existing rows
>>>>>>> test-fe2
    op.execute("UPDATE documents SET title = 'Untitled' WHERE title IS NULL")
    op.execute(
        "UPDATE documents SET original_filename = 'unknown' WHERE original_filename IS NULL"
    )

<<<<<<< HEAD
=======
    # Make title and original_filename NOT NULL after backfill
>>>>>>> test-fe2
    op.alter_column("documents", "title", nullable=False)
    op.alter_column("documents", "original_filename", nullable=False)


def downgrade() -> None:
<<<<<<< HEAD
    op.drop_column("documents", "vertex_index_id")
=======
>>>>>>> test-fe2
    op.drop_column("documents", "content_type")
    op.drop_column("documents", "file_size")
    op.drop_column("documents", "original_filename")
    op.drop_column("documents", "description")
    op.drop_column("documents", "title")
