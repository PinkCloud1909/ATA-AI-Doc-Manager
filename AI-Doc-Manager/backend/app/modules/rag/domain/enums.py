"""Enums for the RAG ingestion lifecycle."""

from enum import Enum


class RagIngestionStatus(str, Enum):
    """Lifecycle of a document's ingestion into the RAG Engine corpus.

    Transitions::

        NOT_INGESTED ─→ PENDING ─→ INGESTING ─→ COMPLETED
                            │           │            │
                            │           └─→ FAILED ──┤ (retry → INGESTING)
                            │                        │
                            └────────────────────────┴─→ NOT_INGESTED (delete)

    ``PENDING`` means a Cloud Tasks ingestion task has been enqueued but has
    not started yet (async mode only).  In synchronous mode documents move
    straight from ``NOT_INGESTED`` to ``INGESTING``.
    """

    NOT_INGESTED = "not_ingested"
    PENDING = "pending"
    INGESTING = "ingesting"
    COMPLETED = "completed"
    FAILED = "failed"
