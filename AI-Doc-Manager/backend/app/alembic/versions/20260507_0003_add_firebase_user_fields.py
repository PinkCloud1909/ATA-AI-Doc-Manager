"""add firebase user fields

Revision ID: 20260507_0003
Revises: 20260423_0002
Create Date: 2026-05-07 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260507_0003"
down_revision: str | None = "20260423_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column(
        "users", sa.Column("firebase_uid", sa.String(length=128), nullable=True)
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_firebase_uid", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "firebase_uid")
    op.drop_column("users", "email")
