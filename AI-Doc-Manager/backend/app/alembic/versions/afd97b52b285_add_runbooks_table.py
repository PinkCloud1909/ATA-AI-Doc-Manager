"""add_runbooks_table

Revision ID: afd97b52b285
Revises: 20260501_0003
Create Date: 2026-06-03 17:50:46.968372
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "afd97b52b285"
down_revision: str | None = "20260501_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "runbooks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("purpose", sa.String(length=100), nullable=False),
        sa.Column("document_ids", sa.JSON(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="generating"
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name=op.f("fk_runbooks_created_by_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("runbooks_pkey")),
    )
    op.create_index(
        op.f("ix_runbooks_created_by"), "runbooks", ["created_by"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_runbooks_created_by"), table_name="runbooks")
    op.drop_table("runbooks")
