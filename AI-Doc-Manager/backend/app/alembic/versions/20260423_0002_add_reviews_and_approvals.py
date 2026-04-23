"""add reviews and approval metadata

Revision ID: 20260423_0002
Revises: 20260420_0001
Create Date: 2026-04-23 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260423_0002"
down_revision: str | None = "20260420_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'pending_review'")
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'approved'")
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'rejected'")
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'expired'")

    op.add_column(
        "documents",
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("documents", sa.Column("submitted_at", sa.TIMESTAMP(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("documents", sa.Column("approved_at", sa.TIMESTAMP(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("rejected_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("documents", sa.Column("rejected_reason", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("rejected_at", sa.TIMESTAMP(), nullable=True))

    op.create_foreign_key(
        "fk_documents_submitted_by_users",
        "documents",
        "users",
        ["submitted_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_documents_approved_by_users",
        "documents",
        "users",
        ["approved_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_documents_rejected_by_users",
        "documents",
        "users",
        ["rejected_by"],
        ["id"],
    )
    op.create_index("ix_documents_submitted_by", "documents", ["submitted_by"])
    op.create_index("ix_documents_approved_by", "documents", ["approved_by"])
    op.create_index("ix_documents_rejected_by", "documents", ["rejected_by"])

    op.alter_column(
        "document_reviews",
        "document_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column(
        "document_reviews",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column(
        "document_reviews",
        "grade",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_check_constraint(
        "ck_document_reviews_grade",
        "document_reviews",
        "grade BETWEEN 1 AND 10",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_document_reviews_grade",
        "document_reviews",
        type_="check",
    )
    op.alter_column(
        "document_reviews",
        "grade",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "document_reviews",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.alter_column(
        "document_reviews",
        "document_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )

    op.drop_index("ix_documents_rejected_by", table_name="documents")
    op.drop_index("ix_documents_approved_by", table_name="documents")
    op.drop_index("ix_documents_submitted_by", table_name="documents")
    op.drop_constraint("fk_documents_rejected_by_users", "documents", type_="foreignkey")
    op.drop_constraint("fk_documents_approved_by_users", "documents", type_="foreignkey")
    op.drop_constraint("fk_documents_submitted_by_users", "documents", type_="foreignkey")
    op.drop_column("documents", "rejected_at")
    op.drop_column("documents", "rejected_reason")
    op.drop_column("documents", "rejected_by")
    op.drop_column("documents", "approved_at")
    op.drop_column("documents", "approved_by")
    op.drop_column("documents", "submitted_at")
    op.drop_column("documents", "submitted_by")

    # status_enum retains added values for forward compatibility
