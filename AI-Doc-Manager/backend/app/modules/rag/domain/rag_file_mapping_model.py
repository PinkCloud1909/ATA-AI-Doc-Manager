"""SQLAlchemy ORM model for tracking document → RAG file mappings.

Every approved document is imported into a RAG Engine corpus via the
``ImportRagFiles`` API.  This table stores the mapping between the document's
PostgreSQL UUID and the RAG Engine's server-generated ``rag_file_id`` so that
downstream operations (delete, re-ingest, scoped retrieval) can find the
correct RAG file without scanning the entire corpus.

Ingestion *status* lives on ``documents.rag_ingestion_status`` — a mapping row
exists only for documents whose import succeeded.

.. note::

    The ``document_id`` column is a soft reference (UUID, no ``ForeignKey``
    constraint at the ORM level).  The actual FK (CASCADE) is declared in the
    Alembic migration.  This avoids a circular import through
    ``model_registry`` → ``Base`` metadata.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RagFileMapping(Base):
    __tablename__ = "rag_file_mappings"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "rag_corpus_resource",
            name="uq_rag_file_mappings_doc_corpus",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    rag_corpus_resource: Mapped[str] = mapped_column(Text, nullable=False)
    rag_file_id: Mapped[str] = mapped_column(String(200), nullable=False)
    rag_file_resource: Mapped[str] = mapped_column(Text, nullable=False)
    imported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
