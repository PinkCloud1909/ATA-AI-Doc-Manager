"""Unit tests for VertexVectorAdapter.

All Vertex AI SDK calls and database sessions are mocked so these tests run
offline without any GCP credentials or database.

Coverage:
- upsert_document: happy path, skips when index is None
- semantic_search: returns resolved chunks, handles empty response,
  skips when endpoint is not configured, handles stale datapoint IDs
- delete_document: deletes correct datapoint IDs, no-op when no chunks
- _resolve_neighbors: parses IDs, batch-fetches from DB, skips bad IDs
"""

import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_settings(**overrides):
    """Return a minimal Settings-like object for the adapter."""
    defaults = {
        "gcp_project_id": "test-project",
        "gcp_location": "us-central1",
        "vertex_index_id": "idx-001",
        "vertex_index_endpoint_id": "ep-001",
        "vertex_deployed_index_id": "dep-001",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_chunk(document_id: uuid.UUID, chunk_index: int, text: str):
    """Return a minimal DocumentChunk-like object."""
    return SimpleNamespace(
        id=uuid.uuid4(),
        document_id=document_id,
        chunk_index=chunk_index,
        text=text,
        embedding_model="gemini-embedding-2",
        vectorized_at=datetime(2026, 7, 1),
    )


def _make_neighbor(datapoint_id: str, distance: float = 0.85):
    """Return a neighbour-like object from find_neighbors response."""
    n = MagicMock()
    n.id = datapoint_id
    n.distance = distance
    return n


# ---------------------------------------------------------------------------
# Helpers to build a VertexVectorAdapter with mocked dependencies
# ---------------------------------------------------------------------------

_AIPLATFORM_PATH = "app.shared.adapters.vertex_vector_adapter.aiplatform"
_DB_SESSION_PATH = "app.shared.adapters.vertex_vector_adapter.get_db_session"


@pytest.fixture()
def mock_aiplatform():
    """Patch the entire aiplatform module inside the adapter."""
    with patch(_AIPLATFORM_PATH) as mock_ai:
        # Mocked index and endpoint instances
        mock_index = MagicMock(name="MatchingEngineIndex")
        mock_endpoint = MagicMock(name="MatchingEngineIndexEndpoint")

        mock_ai.MatchingEngineIndex.return_value = mock_index
        mock_ai.MatchingEngineIndexEndpoint.return_value = mock_endpoint
        mock_ai.matching_engine.matching_engine_index_config.IndexDatapoint = MagicMock(
            name="IndexDatapoint",
            side_effect=lambda **kw: SimpleNamespace(**kw),
        )
        # Expose sub-objects for assertions
        mock_ai._mock_index = mock_index
        mock_ai._mock_endpoint = mock_endpoint
        yield mock_ai


@pytest.fixture()
def adapter(mock_aiplatform):
    """Return a VertexVectorAdapter with mocked aiplatform."""
    from app.shared.adapters.vertex_vector_adapter import VertexVectorAdapter

    settings = _make_settings()
    a = VertexVectorAdapter(settings=settings)
    # Attach convenience references for tests
    a._mock_index = mock_aiplatform._mock_index
    a._mock_endpoint = mock_aiplatform._mock_endpoint
    return a


# ---------------------------------------------------------------------------
# upsert_document tests
# ---------------------------------------------------------------------------


class TestUpsertDocument:
    def test_upserts_correct_datapoint_ids(self, adapter):
        doc_id = str(uuid.uuid4())
        chunks = ["chunk 0", "chunk 1", "chunk 2"]
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

        adapter.upsert_document(doc_id, chunks, embeddings)

        adapter._mock_index.upsert_datapoints.assert_called_once()
        datapoints = adapter._mock_index.upsert_datapoints.call_args.kwargs["datapoints"]
        assert len(datapoints) == 3
        ids = [dp.datapoint_id for dp in datapoints]
        assert ids == [f"{doc_id}_0", f"{doc_id}_1", f"{doc_id}_2"]

    def test_skips_when_index_is_none(self, adapter):
        adapter.index = None
        adapter.upsert_document("doc-1", ["text"], [[0.1]])
        # Should not raise, upsert_datapoints should not be called
        adapter._mock_index.upsert_datapoints.assert_not_called()

    def test_skips_when_no_chunks(self, adapter):
        adapter.upsert_document("doc-1", [], [])
        adapter._mock_index.upsert_datapoints.assert_not_called()


# ---------------------------------------------------------------------------
# semantic_search tests
# ---------------------------------------------------------------------------


class TestSemanticSearch:
    def _make_session(self, chunks: list):
        """Return a mock SQLAlchemy Session that returns *chunks* on query."""
        session = MagicMock()
        # The adapter calls: list(session.execute(...).scalars())
        # so .scalars() must be iterable.
        scalars_result = MagicMock()
        scalars_result.__iter__ = MagicMock(return_value=iter(chunks))
        execute_result = MagicMock()
        execute_result.scalars.return_value = scalars_result
        session.execute.return_value = execute_result
        return session

    def _patch_db(self, chunks: list):
        """Context manager that patches get_db_session to yield a mock session."""
        session = self._make_session(chunks)
        gen = iter([session])
        return patch(_DB_SESSION_PATH, return_value=gen)

    def test_returns_resolved_text(self, adapter):
        doc_id = uuid.uuid4()
        neighbor = _make_neighbor(f"{doc_id}_0", distance=0.9)
        adapter._mock_endpoint.find_neighbors.return_value = [[neighbor]]

        chunk = _make_chunk(doc_id, 0, "The quick brown fox")

        with self._patch_db([chunk]):
            results = adapter.semantic_search([0.1, 0.2], top_k=1)

        assert len(results) == 1
        assert results[0]["text"] == "The quick brown fox"
        assert results[0]["score"] == pytest.approx(0.9)
        assert results[0]["metadata"]["chunk_index"] == 0
        assert results[0]["metadata"]["document_id"] == str(doc_id)

    def test_returns_empty_when_no_response(self, adapter):
        adapter._mock_endpoint.find_neighbors.return_value = [[]]
        with self._patch_db([]):
            results = adapter.semantic_search([0.1])
        assert results == []

    def test_returns_empty_when_endpoint_not_configured(self, adapter):
        adapter.index_endpoint = None
        results = adapter.semantic_search([0.1])
        assert results == []

    def test_skips_stale_datapoints(self, adapter):
        doc_id = uuid.uuid4()
        # find_neighbors returns a neighbor but there is no matching DB row
        neighbor = _make_neighbor(f"{doc_id}_99", distance=0.7)
        adapter._mock_endpoint.find_neighbors.return_value = [[neighbor]]

        with self._patch_db([]):  # no chunks in DB
            results = adapter.semantic_search([0.1])

        assert results == []

    def test_skips_bad_datapoint_ids(self, adapter):
        bad_neighbor = _make_neighbor("no_underscore_at_start", distance=0.5)
        # last rfind("_") will parse but UUID will fail
        adapter._mock_endpoint.find_neighbors.return_value = [[bad_neighbor]]
        with self._patch_db([]):
            results = adapter.semantic_search([0.1])
        assert results == []

    def test_handles_find_neighbors_exception(self, adapter):
        adapter._mock_endpoint.find_neighbors.side_effect = RuntimeError("quota exceeded")
        with self._patch_db([]):
            results = adapter.semantic_search([0.1])
        assert results == []


# ---------------------------------------------------------------------------
# delete_document tests
# ---------------------------------------------------------------------------


class TestDeleteDocument:
    def _make_session_with_indices(self, chunk_indices: list[int]):
        session = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.__iter__ = MagicMock(return_value=iter(chunk_indices))
        execute_mock = MagicMock()
        execute_mock.scalars.return_value = scalars_mock
        session.execute.return_value = execute_mock
        return session

    def _patch_db_with_indices(self, chunk_indices: list[int]):
        session = self._make_session_with_indices(chunk_indices)
        gen = iter([session])
        return patch(_DB_SESSION_PATH, return_value=gen)

    def test_removes_correct_datapoint_ids(self, adapter):
        doc_id = str(uuid.uuid4())
        with self._patch_db_with_indices([0, 1, 2]):
            adapter.delete_document(doc_id)

        adapter._mock_index.remove_datapoints.assert_called_once()
        removed_ids = adapter._mock_index.remove_datapoints.call_args.kwargs["datapoint_ids"]
        assert sorted(removed_ids) == sorted(
            [f"{doc_id}_0", f"{doc_id}_1", f"{doc_id}_2"]
        )

    def test_noop_when_no_chunks_in_db(self, adapter):
        doc_id = str(uuid.uuid4())
        with self._patch_db_with_indices([]):
            adapter.delete_document(doc_id)
        adapter._mock_index.remove_datapoints.assert_not_called()

    def test_noop_when_index_is_none(self, adapter):
        adapter.index = None
        # Should not raise or try to access DB
        with patch(_DB_SESSION_PATH) as mock_db:
            adapter.delete_document(str(uuid.uuid4()))
            mock_db.assert_not_called()
