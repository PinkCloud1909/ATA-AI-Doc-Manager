"""Initial schema — consolidated from all prior migrations.

Creates the complete database schema in a single migration:
- Enum types: document_type_enum, status_enum
- Tables: roles, users, privileges, user_roles, documents,
  document_reviews, runbooks, document_chunks, rag_file_mappings

Revision ID: 00000001_0001
Revises:
Create Date: 2026-07-13 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "00000001_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ── PostgreSQL enum type definitions ──────────────────────────────────────
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
    "pending_review",
    "approved",
    "rejected",
    "expired",
    "active",
    "archived",
    name="status_enum",
    create_type=False,
)


def upgrade() -> None:
    # ── 1. Create enum types first (must exist before tables reference them) ──
    bind = op.get_bind()
    document_type_enum.create(bind, checkfirst=True)
    status_enum.create(bind, checkfirst=True)

    # ── 2. Tables in dependency order ────────────────────────────────────

    # -- roles --
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role_name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("roles_pkey")),
        sa.UniqueConstraint("role_name", name="uq_roles_role_name"),
    )

    # -- users --
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("last_password_changed", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("users_pkey")),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    # -- privileges --
    op.create_table(
        "privileges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=True),
        sa.Column("api_endpoint", sa.String(length=255), nullable=False),
        sa.Column("is_allowed", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"],
            name=op.f("fk_privileges_role_id_roles"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("privileges_pkey")),
    )
    op.create_index("ix_privileges_role_id", "privileges", ["role_id"])

    # -- user_roles --
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_by", sa.Uuid(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_by"], ["users.id"],
            name=op.f("fk_user_roles_assigned_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"],
            name=op.f("fk_user_roles_role_id_roles"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name=op.f("fk_user_roles_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("user_roles_pkey")),
    )
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])

    # -- documents --
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_group_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("file_link", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("content_type", sa.String(length=200), nullable=True),
        sa.Column("is_vectorized", sa.Boolean(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.Uuid(), nullable=True),
        sa.Column("modified_date", sa.DateTime(), nullable=True),
        sa.Column("submitted_by", sa.Uuid(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.Uuid(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_by", sa.Uuid(), nullable=True),
        sa.Column("rejected_reason", sa.Text(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["users.id"],
            name=op.f("fk_documents_approved_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"],
            name=op.f("fk_documents_created_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["modified_by"], ["users.id"],
            name=op.f("fk_documents_modified_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["rejected_by"], ["users.id"],
            name=op.f("fk_documents_rejected_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["submitted_by"], ["users.id"],
            name=op.f("fk_documents_submitted_by_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("documents_pkey")),
        sa.UniqueConstraint(
            "document_group_id", "version",
            name="uq_documents_group_version",
        ),
    )
    op.create_index("ix_documents_approved_by", "documents", ["approved_by"])
    op.create_index("ix_documents_created_by", "documents", ["created_by"])
    op.create_index("ix_documents_document_group_id", "documents", ["document_group_id"])
    op.create_index("ix_documents_modified_by", "documents", ["modified_by"])
    op.create_index("ix_documents_rejected_by", "documents", ["rejected_by"])
    op.create_index("ix_documents_submitted_by", "documents", ["submitted_by"])

    # -- document_reviews --
    op.create_table(
        "document_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "grade BETWEEN 1 AND 10",
            name="ck_document_reviews_grade",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name=op.f("fk_document_reviews_document_id_documents"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name=op.f("fk_document_reviews_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("document_reviews_pkey")),
    )
    op.create_index(
        "ix_document_reviews_document_id", "document_reviews", ["document_id"],
    )
    op.create_index(
        "ix_document_reviews_user_id", "document_reviews", ["user_id"],
    )

    # -- runbooks --
    op.create_table(
        "runbooks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("purpose", sa.String(length=100), nullable=False),
        sa.Column("document_ids", sa.JSON(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="generating",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"],
            name=op.f("fk_runbooks_created_by_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("runbooks_pkey")),
    )
    op.create_index("ix_runbooks_created_by", "runbooks", ["created_by"])

    # -- document_chunks --
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("source_uri", sa.String(length=1000), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section", sa.String(length=500), nullable=True),
        sa.Column("embedding_model", sa.String(length=200), nullable=False),
        sa.Column("embedding_task_type", sa.String(length=100), nullable=False),
        sa.Column("vector_datapoint_id", sa.String(length=700), nullable=False),
        sa.Column("vectorized_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name=op.f("fk_document_chunks_document_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("document_chunks_pkey")),
        sa.UniqueConstraint(
            "document_id", "chunk_index",
            name="uq_document_chunks_doc_chunk",
        ),
        sa.UniqueConstraint(
            "vector_datapoint_id",
            name="uq_document_chunks_vector_datapoint",
        ),
    )
    op.create_index(
        "ix_document_chunks_document_id", "document_chunks", ["document_id"],
    )
    op.create_index(
        "ix_document_chunks_vector_datapoint_id",
        "document_chunks",
        ["vector_datapoint_id"],
    )

    # -- rag_file_mappings --
    op.create_table(
        "rag_file_mappings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("rag_corpus_resource", sa.Text(), nullable=False),
        sa.Column("rag_file_id", sa.String(length=200), nullable=False),
        sa.Column("rag_file_resource", sa.Text(), nullable=False),
        sa.Column("imported_file_count", sa.Integer(), nullable=True),
        sa.Column(
            "import_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name=op.f("fk_rag_file_mappings_document_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("rag_file_mappings_pkey")),
        sa.UniqueConstraint(
            "document_id", "rag_corpus_resource",
            name="uq_rag_file_mappings_doc_corpus",
        ),
    )
    op.create_index(
        "ix_rag_file_mappings_document_id",
        "rag_file_mappings",
        ["document_id"],
    )


def downgrade() -> None:
    # ── Drop tables in reverse dependency order ───────────────────────────
    op.drop_index("ix_rag_file_mappings_document_id", table_name="rag_file_mappings")
    op.drop_table("rag_file_mappings")

    op.drop_index(
        "ix_document_chunks_vector_datapoint_id", table_name="document_chunks",
    )
    op.drop_index(
        "ix_document_chunks_document_id", table_name="document_chunks",
    )
    op.drop_table("document_chunks")

    op.drop_index("ix_runbooks_created_by", table_name="runbooks")
    op.drop_table("runbooks")

    op.drop_index(
        "ix_document_reviews_user_id", table_name="document_reviews",
    )
    op.drop_index(
        "ix_document_reviews_document_id", table_name="document_reviews",
    )
    op.drop_table("document_reviews")

    op.drop_index("ix_documents_submitted_by", table_name="documents")
    op.drop_index("ix_documents_rejected_by", table_name="documents")
    op.drop_index("ix_documents_modified_by", table_name="documents")
    op.drop_index("ix_documents_document_group_id", table_name="documents")
    op.drop_index("ix_documents_created_by", table_name="documents")
    op.drop_index("ix_documents_approved_by", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index("ix_privileges_role_id", table_name="privileges")
    op.drop_table("privileges")

    op.drop_table("users")
    op.drop_table("roles")

    # ── Drop enum types ──────────────────────────────────────────────────
    bind = op.get_bind()
    status_enum.drop(bind, checkfirst=True)
    document_type_enum.drop(bind, checkfirst=True)
