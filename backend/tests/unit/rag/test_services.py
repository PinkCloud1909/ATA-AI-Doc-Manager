"""Unit tests for the RAG ingestion orchestration service.

The RAG engine adapter and the database session are mocked — these tests
verify status transitions, force re-ingest behaviour, error persistence,
and transaction commits.
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import app.core.db  # noqa: F401 — must load before domain models (registry bootstrap)

from app.core.exceptions import ExternalServiceError, NotFoundError
from app.modules.rag.application.services import (
    delete_document_ingestion,
    get_ingestion_status,
    ingest_document,
    mark_ingestion_pending,
)
from app.modules.rag.domain.enums import RagIngestionStatus
from app.shared.interfaces import RagIngestResult


def _mock_document(status=RagIngestionStatus.NOT_INGESTED):
    return SimpleNamespace(
        id=uuid.uuid4(),
        title="Test Doc",
        file_link="gcs://bucket/docs/test.pdf",
        content_type="application/pdf",
        rag_ingestion_status=status,
        rag_ingestion_error=None,
        rag_ingested_at=None,
        modified_date=None,
    )


def _mock_rag_engine():
    engine = MagicMock()
    engine.corpus_name = "projects/p/locations/l/ragCorpora/123"
    engine.ingest_file.return_value = RagIngestResult(
        rag_file_id="456",
        rag_file_resource="projects/p/locations/l/ragCorpora/123/ragFiles/456",
        imported_count=1,
        skipped_count=0,
        failed_count=0,
    )
    return engine


def _session_returning(document, mapping=None):
    """Build a session mock whose scalar_one_or_none alternates: doc, mapping."""
    session = MagicMock()
    # _get_document and _get_existing_mapping / _upsert_mapping each execute
    # a select; return doc first, then mapping for subsequent calls.
    results = [document, mapping, mapping, mapping]
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.side_effect = results
    session.execute.return_value = execute_result
    return session


class TestIngestDocument:
    def test_success_sets_completed(self):
        doc = _mock_document()
        session = _session_returning(doc)
        engine = _mock_rag_engine()

        result = ingest_document(session, doc.id, engine, settings=MagicMock())

        assert result.status == RagIngestionStatus.COMPLETED.value
        assert result.rag_file_id == "456"
        assert doc.rag_ingestion_status == RagIngestionStatus.COMPLETED
        assert doc.rag_ingested_at is not None
        assert doc.rag_ingestion_error is None
        engine.ingest_file.assert_called_once_with(
            document_id=str(doc.id),
            gcs_uri=doc.file_link,
            display_name=doc.title,
        )
        assert session.commit.called

    def test_completed_early_return_without_force(self):
        doc = _mock_document(status=RagIngestionStatus.COMPLETED)
        session = _session_returning(doc)
        engine = _mock_rag_engine()

        result = ingest_document(session, doc.id, engine, settings=MagicMock())

        assert result.status == RagIngestionStatus.COMPLETED.value
        assert "already ingested" in result.message
        engine.ingest_file.assert_not_called()

    def test_force_deletes_existing_rag_file_first(self):
        doc = _mock_document(status=RagIngestionStatus.COMPLETED)
        old_resource = "projects/p/l/ragCorpora/123/ragFiles/old"
        mapping = SimpleNamespace(rag_file_resource=old_resource)
        session = _session_returning(doc, mapping)
        engine = _mock_rag_engine()

        result = ingest_document(
            session, doc.id, engine, settings=MagicMock(), force=True
        )

        engine.delete_file.assert_called_once_with(old_resource)
        engine.ingest_file.assert_called_once()
        assert result.status == RagIngestionStatus.COMPLETED.value

    def test_failure_sets_failed_and_persists_error(self):
        doc = _mock_document()
        session = _session_returning(doc)
        engine = _mock_rag_engine()
        engine.ingest_file.side_effect = ExternalServiceError("Import exploded")

        with pytest.raises(ExternalServiceError, match="Import exploded"):
            ingest_document(session, doc.id, engine, settings=MagicMock())

        assert doc.rag_ingestion_status == RagIngestionStatus.FAILED
        assert "Import exploded" in doc.rag_ingestion_error
        assert session.commit.called

    def test_document_not_found_raises(self):
        session = _session_returning(None)
        engine = _mock_rag_engine()

        with pytest.raises(NotFoundError, match="Document not found"):
            ingest_document(session, uuid.uuid4(), engine, settings=MagicMock())


class TestMarkIngestionPending:
    def test_sets_pending(self):
        doc = _mock_document()
        session = _session_returning(doc)

        mark_ingestion_pending(session, doc.id)

        assert doc.rag_ingestion_status == RagIngestionStatus.PENDING
        assert session.commit.called


class TestDeleteDocumentIngestion:
    def test_deletes_rag_file_and_resets_status(self):
        doc = _mock_document(status=RagIngestionStatus.COMPLETED)
        mapping = SimpleNamespace(
            rag_file_resource="projects/p/l/ragCorpora/123/ragFiles/456",
        )
        session = _session_returning(doc, mapping)
        engine = _mock_rag_engine()

        delete_document_ingestion(session, doc.id, engine)

        engine.delete_file.assert_called_once_with(mapping.rag_file_resource)
        session.delete.assert_called_once_with(mapping)
        assert doc.rag_ingestion_status == RagIngestionStatus.NOT_INGESTED
        assert doc.rag_ingested_at is None
        assert doc.rag_ingestion_error is None

    def test_noop_when_no_mapping(self):
        doc = _mock_document(status=RagIngestionStatus.FAILED)
        session = _session_returning(doc, None)
        engine = _mock_rag_engine()

        delete_document_ingestion(session, doc.id, engine)

        engine.delete_file.assert_not_called()
        assert doc.rag_ingestion_status == RagIngestionStatus.NOT_INGESTED


class TestGetIngestionStatus:
    def test_returns_status_dict(self):
        doc = _mock_document(status=RagIngestionStatus.COMPLETED)
        session = _session_returning(doc)

        status = get_ingestion_status(session, doc.id)

        assert status["document_id"] == doc.id
        assert status["status"] == "completed"
        assert status["title"] == "Test Doc"
