"""initial schema

Revision ID: 20260420_0001
Revises:
Create Date: 2026-04-20 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260420_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

document_type_enum = postgresql.ENUM(
    "policy",
    "manual",
    "report",
    "other",
    name="document_type_enum",
    create_type=False,
)
status_enum = postgresql.ENUM(
    "draft",
    "active",
    "archived",
    name="status_enum",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    document_type_enum.create(bind, checkfirst=True)
    status_enum.create(bind, checkfirst=True)

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_name", name="uq_roles_role_name"),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("last_password_changed", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_table(
        "privileges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("api_endpoint", sa.String(length=255), nullable=False),
        sa.Column("is_allowed", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_privileges_role_id", "privileges", ["role_id"], unique=False)

    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"], unique=False)
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("file_link", sa.String(length=500), nullable=False),
        sa.Column("is_vectorized", sa.Boolean(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("modified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("modified_date", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["modified_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document_group_id",
            "version",
            name="uq_documents_group_version",
        ),
    )
    op.create_index(
        "ix_documents_created_by",
        "documents",
        ["created_by"],
        unique=False,
    )
    op.create_index(
        "ix_documents_document_group_id",
        "documents",
        ["document_group_id"],
        unique=False,
    )
    op.create_index(
        "ix_documents_modified_by",
        "documents",
        ["modified_by"],
        unique=False,
    )

    op.create_table(
        "document_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_date", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_document_reviews_document_id",
        "document_reviews",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        "ix_document_reviews_user_id",
        "document_reviews",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_document_reviews_user_id", table_name="document_reviews")
    op.drop_index("ix_document_reviews_document_id", table_name="document_reviews")
    op.drop_table("document_reviews")

    op.drop_index("ix_documents_modified_by", table_name="documents")
    op.drop_index("ix_documents_document_group_id", table_name="documents")
    op.drop_index("ix_documents_created_by", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index("ix_privileges_role_id", table_name="privileges")
    op.drop_table("privileges")

    op.drop_table("users")
    op.drop_table("roles")

    bind = op.get_bind()
    status_enum.drop(bind, checkfirst=True)
    document_type_enum.drop(bind, checkfirst=True)
