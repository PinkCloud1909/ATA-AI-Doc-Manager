"""SQLAlchemy ORM model for document_chunks.

Each row represents one text chunk that was extracted from a document during
vectorization.  The primary key ``id`` is a UUID, and the pair
(document_id, chunk_index) is unique so rows can be upserted safely.

Datapoint ID contract
---------------------
Vertex AI Vector Search datapoint IDs are built as::

    f"{document_id}_{chunk_index}"

This matches the pattern used in VertexVectorAdapter.upsert_document and
semantic_search.  When ``find_neighbors`` returns a datapoint ID, we split on
the last underscore to recover ``document_id`` and ``chunk_index``, then fetch
the matching row from this table.

ChromaDB note
-------------
ChromaDB stores text inline in the collection, so this table is only populated
when the Vertex adapter is active (ENVIRONMENT=production).  The ChromaDB
adapter ignores this table entirely.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "chunk_index", name="uq_document_chunks_doc_chunk"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # Soft reference to documents.id (no FK constraint so rows survive document
    # soft-deletes and to avoid circular-import issues across modules).
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    # Zero-based position; matches the numeric suffix in the Vertex datapoint ID.
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(200), nullable=False)
    vectorized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
