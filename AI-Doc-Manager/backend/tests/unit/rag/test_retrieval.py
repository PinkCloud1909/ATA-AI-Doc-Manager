"""Unit tests for the RAG retrieval service (title enrichment + filtering)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import ExternalServiceError
from app.modules.rag.application.retrieval import retrieve_chunks
from app.shared.interfaces import RetrievedChunk


_RETRIEVAL = "app.modules.rag.application.retrieval"


def _chunk(rag_file_id="456", text="chunk text"):
    return RetrievedChunk(
        text=text,
        source_uri="gs://bucket/doc.pdf",
        rag_file_id=rag_file_id,
        score=0.8,
        distance=0.2,
    )


class TestRetrieveChunks:
    @patch(f"{_RETRIEVAL}._enrich_chunks")
    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_basic_retrieval(self, mock_get_engine, mock_enrich):
        engine = MagicMock()
        engine.retrieve.return_value = [_chunk()]
        mock_get_engine.return_value = engine

        results = retrieve_chunks("query", top_k=5)

        assert len(results) == 1
        engine.retrieve.assert_called_once_with(
            query_text="query", top_k=5, rag_file_ids=None
        )
        mock_enrich.assert_called_once()

    @patch(f"{_RETRIEVAL}._resolve_rag_file_ids")
    @patch(f"{_RETRIEVAL}.session_scope")
    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_empty_filter_returns_empty_without_search(
        self, mock_get_engine, mock_scope, mock_resolve
    ):
        """No matching mappings → [] immediately, NOT a whole-corpus search."""
        engine = MagicMock()
        mock_get_engine.return_value = engine
        mock_resolve.return_value = []
        mock_scope.return_value.__enter__.return_value = MagicMock()

        results = retrieve_chunks("query", top_k=5, document_ids=[uuid.uuid4()])

        assert results == []
        engine.retrieve.assert_not_called()

    @patch(f"{_RETRIEVAL}._enrich_chunks")
    @patch(f"{_RETRIEVAL}._resolve_rag_file_ids")
    @patch(f"{_RETRIEVAL}.session_scope")
    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_filter_resolved_to_rag_file_ids(
        self, mock_get_engine, mock_scope, mock_resolve, mock_enrich
    ):
        engine = MagicMock()
        engine.retrieve.return_value = [_chunk()]
        mock_get_engine.return_value = engine
        mock_resolve.return_value = ["456", "789"]
        mock_scope.return_value.__enter__.return_value = MagicMock()

        doc_ids = [uuid.uuid4(), uuid.uuid4()]
        retrieve_chunks("query", top_k=10, document_ids=doc_ids)

        engine.retrieve.assert_called_once_with(
            query_text="query", top_k=10, rag_file_ids=["456", "789"]
        )

    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_exception_propagates(self, mock_get_engine):
        engine = MagicMock()
        engine.retrieve.side_effect = ExternalServiceError("outage")
        mock_get_engine.return_value = engine

        with pytest.raises(ExternalServiceError, match="outage"):
            retrieve_chunks("query")

    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_empty_results_no_enrichment(self, mock_get_engine):
        engine = MagicMock()
        engine.retrieve.return_value = []
        mock_get_engine.return_value = engine

        assert retrieve_chunks("query") == []


class TestEnrichment:
    @patch(f"{_RETRIEVAL}.session_scope")
    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_chunks_enriched_with_document_titles(self, mock_get_engine, mock_scope):
        doc_id = uuid.uuid4()
        engine = MagicMock()
        engine.retrieve.return_value = [_chunk(rag_file_id="456")]
        mock_get_engine.return_value = engine

        session = MagicMock()
        session.execute.return_value = [("456", doc_id, "Q4 Security Policy")]
        mock_scope.return_value.__enter__.return_value = session

        results = retrieve_chunks("query")

        assert results[0].document_id == doc_id
        assert results[0].document_title == "Q4 Security Policy"

    @patch(f"{_RETRIEVAL}.session_scope")
    @patch(f"{_RETRIEVAL}.get_rag_engine")
    def test_unmapped_chunks_keep_none_title(self, mock_get_engine, mock_scope):
        engine = MagicMock()
        engine.retrieve.return_value = [_chunk(rag_file_id="999")]
        mock_get_engine.return_value = engine

        session = MagicMock()
        session.execute.return_value = []  # no mapping rows found
        mock_scope.return_value.__enter__.return_value = session

        results = retrieve_chunks("query")

        assert results[0].document_title is None
        assert results[0].document_id is None
