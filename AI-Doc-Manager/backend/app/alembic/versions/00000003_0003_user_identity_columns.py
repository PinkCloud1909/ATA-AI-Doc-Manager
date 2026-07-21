"""Add user identity columns present in the ORM model.

Revision ID: 00000003_0003
Revises: 00000002_0002
Create Date: 2026-07-21 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00000003_0003"
down_revision: str | None = "00000002_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column(
        "users", sa.Column("firebase_uid", sa.String(length=128), nullable=True)
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_firebase_uid", "users", ["firebase_uid"])


def downgrade() -> None:
    op.drop_constraint("uq_users_firebase_uid", "users", type_="unique")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_column("users", "firebase_uid")
    op.drop_column("users", "email")
