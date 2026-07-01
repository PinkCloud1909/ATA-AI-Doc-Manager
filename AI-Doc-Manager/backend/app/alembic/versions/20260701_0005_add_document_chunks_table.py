"""add document_chunks table

Revision ID: 20260701_0005
Revises: afd97b52b285
Create Date: 2026-07-01 00:00:00

Why this table exists
---------------------
Vertex AI Vector Search stores only numeric vectors and string datapoint IDs.
It does NOT store the original text.  To serve actual text in semantic-search
results we maintain a ``document_chunks`` table that maps every datapoint ID
back to its source text and metadata.

Datapoint ID format: ``{document_id}_{chunk_index}``  (e.g. ``abc-123_0``)

On upsert the vectorization service writes rows here BEFORE pushing vectors to
Vertex, so the text is always available when ``find_neighbors`` returns IDs.

The ChromaDB adapter stores text directly in the collection and therefore does
NOT use this table - it is a production-only concern.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260701_0005"
down_revision: str | None = "afd97b52b285"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        # Logical owner of this chunk; not a FK so deletes do not cascade
        # automatically - the vector store delete path handles both sides.
        sa.Column("document_id", sa.Uuid(), nullable=False),
        # Zero-based position within the document (matches datapoint ID suffix).
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        # The actual text stored in the vector.  Text is unlimited length
        # because some documents have very large chunks.
        sa.Column("text", sa.Text(), nullable=False),
        # Embedding model name stored for audit / re-vectorization detection.
        sa.Column("embedding_model", sa.String(length=200), nullable=False),
        sa.Column("vectorized_at", sa.DateTime(timezone=False), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("document_chunks_pkey")),
        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name=op.f("uq_document_chunks_doc_chunk"),
        ),
    )
    op.create_index(
        op.f("ix_document_chunks_document_id"),
        "document_chunks",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_document_chunks_document_id"), table_name="document_chunks"
    )
    op.drop_table("document_chunks")
