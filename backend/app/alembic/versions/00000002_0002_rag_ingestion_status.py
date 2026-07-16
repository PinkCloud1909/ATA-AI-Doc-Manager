"""RAG ingestion status — replaces the legacy ``is_vectorized`` flag.

- Adds ``rag_ingestion_status`` / ``rag_ingestion_error`` / ``rag_ingested_at``
  to ``documents`` and backfills ``completed`` from ``is_vectorized``.
- Drops the legacy ``document_chunks`` table (never written since the custom
  chunk/embed pipeline was replaced by Vertex AI RAG Engine).
- Slims ``rag_file_mappings`` down to a pure document ↔ RAG-file pointer
  (``import_status``, ``error_message``, ``imported_file_count`` were never
  meaningfully used — status now lives on ``documents``).
- Removes stale ``/api/v1/vectorization/*`` privilege rows (seeding is
  add-only, so renamed endpoints would otherwise leave orphans behind).

Revision ID: 00000002_0002
Revises: 00000001_0001
Create Date: 2026-07-16 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "00000002_0002"
down_revision: str | None = "00000001_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

rag_ingestion_status_enum = postgresql.ENUM(
    "not_ingested",
    "pending",
    "ingesting",
    "completed",
    "failed",
    name="rag_ingestion_status_enum",
    create_type=False,
)


def upgrade() -> None:
    # ── documents: is_vectorized (bool) → rag ingestion status ────────────
    rag_ingestion_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "documents",
        sa.Column(
            "rag_ingestion_status",
            rag_ingestion_status_enum,
            nullable=False,
            server_default="not_ingested",
        ),
    )
    op.add_column(
        "documents",
        sa.Column("rag_ingestion_error", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("rag_ingested_at", sa.DateTime(), nullable=True),
    )
    op.execute(
        "UPDATE documents "
        "SET rag_ingestion_status = 'completed', rag_ingested_at = modified_date "
        "WHERE is_vectorized IS TRUE"
    )
    op.drop_column("documents", "is_vectorized")

    # ── drop legacy document_chunks (RAG Engine chunks server-side) ───────
    op.drop_index(
        "ix_document_chunks_vector_datapoint_id", table_name="document_chunks",
    )
    op.drop_index(
        "ix_document_chunks_document_id", table_name="document_chunks",
    )
    op.drop_table("document_chunks")

    # ── slim rag_file_mappings to a pure resource pointer ─────────────────
    op.drop_column("rag_file_mappings", "import_status")
    op.drop_column("rag_file_mappings", "error_message")
    op.drop_column("rag_file_mappings", "imported_file_count")

    # ── remove stale privileges for the renamed endpoints ─────────────────
    # Seeding is add-only; the new /api/v1/rag/* privileges are inserted by
    # the seed script on startup.
    op.execute(
        "DELETE FROM privileges "
        "WHERE api_endpoint LIKE '%:/api/v1/vectorization/%'"
    )


def downgrade() -> None:
    # Remove privileges introduced for the renamed endpoints (the old
    # vectorization privileges are restored by re-running the old seed).
    op.execute(
        "DELETE FROM privileges WHERE api_endpoint LIKE '%:/api/v1/rag/%'"
    )

    # ── restore rag_file_mappings columns ──────────────────────────────────
    op.add_column(
        "rag_file_mappings",
        sa.Column("imported_file_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "rag_file_mappings",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "rag_file_mappings",
        sa.Column(
            "import_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
    )
    op.execute("UPDATE rag_file_mappings SET import_status = 'active'")

    # ── restore document_chunks ────────────────────────────────────────────
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

    # ── documents: rag ingestion status → is_vectorized (bool) ────────────
    op.add_column(
        "documents",
        sa.Column("is_vectorized", sa.Boolean(), nullable=True),
    )
    op.execute(
        "UPDATE documents SET is_vectorized = (rag_ingestion_status = 'completed')"
    )
    op.drop_column("documents", "rag_ingested_at")
    op.drop_column("documents", "rag_ingestion_error")
    op.drop_column("documents", "rag_ingestion_status")
    rag_ingestion_status_enum.drop(op.get_bind(), checkfirst=True)
