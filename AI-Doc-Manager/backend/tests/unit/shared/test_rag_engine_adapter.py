"""Unit tests for RagEngineAdapter implementing IRagEngine.

All Vertex AI / RAG Engine SDK calls are mocked via sys.modules injection so
this test suite runs without a GCP project or the real SDK.
"""

from __future__ import annotations

import sys
import uuid
from types import ModuleType
from unittest.mock import ANY, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Inject fake vertexai / vertexai.preview.rag modules into sys.modules
# ---------------------------------------------------------------------------

_mock_vertexai = MagicMock(name="vertexai")
if "vertexai" not in sys.modules:
    sys.modules["vertexai"] = _mock_vertexai

_mock_rag = MagicMock(name="rag")
_mock_corpus = MagicMock(name="RagCorpus")
_mock_corpus.name = "projects/test-proj/locations/us-central1/ragCorpora/123456789"
_mock_rag.create_corpus.return_value = _mock_corpus

_mock_import_response = MagicMock(name="ImportRagFilesResponse")
_mock_import_response.imported_rag_files_count = 5
_mock_import_response.skipped_rag_files_count = 0
_mock_import_response.failed_rag_files_count = 0
_mock_rag.import_files.return_value = _mock_import_response

_mock_file = MagicMock(name="RagFile")
_mock_file.name = "projects/test-proj/locations/us-central1/ragCorpora/123/ragFiles/456"
_mock_file.source_uri = "gs://test-bucket/path/to/doc.pdf"
_mock_rag.list_files.return_value = [_mock_file]

_mock_retrieval_response = MagicMock(name="RetrieveContextsResponse")
_mock_retrieval_response.contexts = MagicMock(name="contexts")
_mock_ctx_1 = MagicMock(name="RagContext")
_mock_ctx_1.text = "Test chunk about system architecture."
_mock_ctx_1.source_uri = "gs://test-bucket/path/to/doc.pdf"
_mock_ctx_1.score = 0.15
_mock_ctx_1.chunk = MagicMock(file_id="456")
_mock_ctx_2 = MagicMock(name="RagContext")
_mock_ctx_2.text = "Another chunk about security best practices."
_mock_ctx_2.source_uri = "gs://test-bucket/path/to/doc.pdf"
_mock_ctx_2.score = 0.35
_mock_ctx_2.chunk = MagicMock(file_id="456")
_mock_retrieval_response.contexts.contexts = [_mock_ctx_1, _mock_ctx_2]
_mock_rag.retrieval_query = MagicMock(name="retrieval_query", return_value=_mock_retrieval_response)
_mock_rag.delete_file.return_value = None

if "vertexai.preview" not in sys.modules:
    sys.modules["vertexai.preview"] = ModuleType("vertexai.preview")
sys.modules["vertexai.preview.rag"] = _mock_rag

_mock_rag.RagManagedVertexVectorSearch = MagicMock(name="RagManagedVertexVectorSearch")
_mock_rag.RagManagedDb = MagicMock(name="RagManagedDb")
_mock_rag.RagVectorDbConfig = MagicMock(name="RagVectorDbConfig")
_mock_rag.RagEmbeddingModelConfig = MagicMock(name="RagEmbeddingModelConfig")
_mock_rag.EmbeddingModelConfig = MagicMock(name="EmbeddingModelConfig")
_mock_rag.VertexPredictionEndpoint = MagicMock(name="VertexPredictionEndpoint")
_mock_rag.TransformationConfig = MagicMock(name="TransformationConfig")
_mock_rag.ChunkingConfig = MagicMock(name="ChunkingConfig")
_mock_rag.RagRetrievalConfig = MagicMock(name="RagRetrievalConfig")
_mock_rag.Filter = MagicMock(name="Filter")
_mock_rag.RagResource = MagicMock(name="RagResource")
_mock_rag.LayoutParserConfig = MagicMock(name="LayoutParserConfig")
_mock_rag.LlmParserConfig = MagicMock(name="LlmParserConfig")

if "google.cloud" not in sys.modules:
    sys.modules["google.cloud"] = ModuleType("google.cloud")
if "google.cloud.aiplatform" not in sys.modules:
    sys.modules["google.cloud.aiplatform"] = MagicMock(name="aiplatform")


def _settings(**overrides) -> object:
    from app.core.config import Settings

    defaults: dict = {
        "gcp_project_id": "test-proj",
        "gcp_location": "us-central1",
        "rag_corpus_resource": None,
        "rag_engine_location": "",
        "rag_embedding_model": "text-embedding-005",
        "rag_chunk_size": 1024,
        "rag_chunk_overlap": 256,
        "rag_layout_parser_enabled": False,
        "rag_layout_parser_processor_name": None,
        "rag_layout_parser_max_parsing_rpm": 120,
        "rag_llm_parser_model": None,
        "rag_max_embedding_requests_per_min": 1000,
        "rag_retrieval_distance_threshold": 0.5,
        "rag_import_timeout_seconds": 600,
        "rag_import_result_sink": None,
        "app_name": "dms-backend",
        "environment": "test",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def _make_adapter(**settings_overrides) -> "RagEngineAdapter":
    from app.shared.adapters.rag_engine_adapter import RagEngineAdapter

    s = _settings(**settings_overrides)
    adapter = RagEngineAdapter(settings=s)
    adapter._sdk_ready = True
    if settings_overrides.pop("init_corpus", True):
        adapter._corpus_name = (
            s.rag_corpus_resource
            or "projects/test-proj/locations/us-central1/ragCorpora/123456789"
        )
    return adapter


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCorpusManagement:
    def test_auto_create_corpus_when_not_configured(self):
        _mock_rag.create_corpus.reset_mock()
        adapter = _make_adapter(rag_corpus_resource=None, init_corpus=False)

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file(
                document_id=str(uuid.uuid4()),
                gcs_uri="gs://test-bucket/path/to/doc.pdf",
            )

        _mock_rag.create_corpus.assert_called_once()
        assert adapter._corpus_name == _mock_corpus.name

    def test_uses_preconfigured_corpus(self):
        _mock_rag.create_corpus.reset_mock()
        configured = "projects/p/locations/l/ragCorpora/preconfigured"
        adapter = _make_adapter(rag_corpus_resource=configured, init_corpus=False)

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file(
                document_id=str(uuid.uuid4()),
                gcs_uri="gs://test-bucket/path/to/doc.pdf",
            )

        _mock_rag.create_corpus.assert_not_called()
        assert adapter._corpus_name == configured


class TestCorpusBackend:
    def test_uses_rag_managed_vertex_vector_search(self):
        _mock_rag.create_corpus.reset_mock()
        _mock_rag.RagManagedVertexVectorSearch.reset_mock()
        adapter = _make_adapter(rag_corpus_resource=None, init_corpus=False)

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file(
                document_id=str(uuid.uuid4()),
                gcs_uri="gs://test-bucket/path/to/doc.pdf",
            )

        _mock_rag.create_corpus.assert_called_once()
        call_kwargs = _mock_rag.create_corpus.call_args.kwargs
        backend_config = call_kwargs.get("backend_config")
        assert backend_config is not None
        vector_db_call = backend_config.vector_db
        _mock_rag.RagManagedVertexVectorSearch.assert_called_once()


class TestLocationValidation:
    def test_us_central1_allowed(self):
        from app.shared.adapters.rag_engine_adapter import RagEngineAdapter
        RagEngineAdapter._validate_location("us-central1")

    def test_other_location_rejected(self):
        from app.core.exceptions import ConfigurationError
        from app.shared.adapters.rag_engine_adapter import RagEngineAdapter
        with pytest.raises(ConfigurationError, match="us-central1"):
            RagEngineAdapter._validate_location("asia-southeast1")


class TestEmbeddingModel:
    def test_embedding_model_in_backend_config(self):
        _mock_rag.create_corpus.reset_mock()
        _mock_rag.EmbeddingModelConfig.reset_mock()

        adapter = _make_adapter(
            rag_corpus_resource=None,
            rag_embedding_model="text-multilingual-embedding-002",
            init_corpus=False,
        )

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file(
                document_id=str(uuid.uuid4()),
                gcs_uri="gs://test-bucket/path/to/doc.pdf",
            )

        # The preview SDK's backend_config path expects the legacy
        # EmbeddingModelConfig(publisher_model=...) shape.
        _mock_rag.EmbeddingModelConfig.assert_called_once_with(
            publisher_model="publishers/google/models/text-multilingual-embedding-002",
        )


class TestIngestFile:
    def test_returns_ingest_result(self):
        doc_id = str(uuid.uuid4())
        adapter = _make_adapter()

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            result = adapter.ingest_file(
                document_id=doc_id,
                gcs_uri="gs://test-bucket/path/to/doc.pdf",
            )

        assert result.rag_file_id is not None
        assert result.imported_count == 5
        assert result.failed_count == 0

    def test_raises_on_missing_source_uri(self):
        adapter = _make_adapter()
        with patch.object(adapter, "_find_rag_file_by_uri", return_value=None):
            from app.core.exceptions import ExternalServiceError
            with pytest.raises(ExternalServiceError):
                adapter.ingest_file(
                    document_id=str(uuid.uuid4()),
                    gcs_uri="gs://test-bucket/nonexistent.pdf",
                )

    def test_raises_on_failed_count(self):
        _mock_rag.import_files.reset_mock()
        failed_response = MagicMock()
        failed_response.imported_rag_files_count = 0
        failed_response.skipped_rag_files_count = 0
        failed_response.failed_rag_files_count = 1
        _mock_rag.import_files.return_value = failed_response

        adapter = _make_adapter()
        from app.core.exceptions import ExternalServiceError
        with pytest.raises(ExternalServiceError, match="1 failed"):
            adapter.ingest_file(
                document_id=str(uuid.uuid4()),
                gcs_uri="gs://test-bucket/bad.pdf",
            )

        _mock_rag.import_files.return_value = _mock_import_response


class TestParserConfigs:
    def test_llm_parser_passed(self):
        _mock_rag.import_files.reset_mock()
        adapter = _make_adapter(rag_llm_parser_model="gemini-2.5-flash")

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file("doc-1", "gs://test-bucket/doc.pdf")

        _mock_rag.LlmParserConfig.assert_called_once_with(model_name="gemini-2.5-flash")

    def test_layout_parser_passed(self):
        _mock_rag.import_files.reset_mock()
        adapter = _make_adapter(
            rag_layout_parser_enabled=True,
            rag_layout_parser_processor_name="projects/p/locations/us/processors/abc",
        )

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file("doc-1", "gs://test-bucket/doc.pdf")

        _mock_rag.LayoutParserConfig.assert_called_once_with(
            processor_name="projects/p/locations/us/processors/abc",
            max_parsing_requests_per_min=120,
        )

    def test_layout_parser_raises_without_processor(self):
        from app.core.exceptions import ConfigurationError
        adapter = _make_adapter(rag_layout_parser_enabled=True, rag_layout_parser_processor_name=None)
        with pytest.raises(ConfigurationError, match="RAG_LAYOUT_PARSER_PROCESSOR_NAME"):
            adapter.ingest_file("doc-1", "gs://test-bucket/doc.pdf")


class TestImportResultSink:
    def test_sink_appended_with_unique_suffix(self):
        _mock_rag.import_files.reset_mock()
        adapter = _make_adapter(rag_import_result_sink="gs://bucket/prefix")

        with patch.object(adapter, "_find_rag_file_by_uri", return_value=_mock_file.name):
            adapter.ingest_file("doc-uuid", "gs://test-bucket/doc.pdf")

        call_kwargs = _mock_rag.import_files.call_args.kwargs
        sink = call_kwargs.get("import_result_sink")
        assert sink is not None
        assert sink.startswith("gs://bucket/prefix/doc-uuid-")
        assert sink.endswith(".ndjson")


class TestRetrieve:
    def test_returns_retrieved_chunks(self):
        adapter = _make_adapter()
        results = adapter.retrieve(query_text="What is the architecture?", top_k=5)

        assert len(results) == 2
        assert results[0].text == "Test chunk about system architecture."
        assert results[0].score == pytest.approx(0.85, abs=0.01)
        assert results[0].rag_file_id == "456"
        assert results[1].score == pytest.approx(0.65, abs=0.01)

    def test_raises_on_empty_rag_file_ids(self):
        adapter = _make_adapter()
        with pytest.raises(ValueError, match="non-empty"):
            adapter.retrieve(query_text="test", top_k=5, rag_file_ids=[])

    def test_empty_response_returns_empty_list(self):
        _mock_empty = MagicMock()
        _mock_empty.contexts = MagicMock()
        _mock_empty.contexts.contexts = []
        _mock_rag.retrieval_query.return_value = _mock_empty

        adapter = _make_adapter()
        results = adapter.retrieve(query_text="nothing", top_k=5)
        assert results == []

        _mock_rag.retrieval_query.return_value = _mock_retrieval_response

    def test_raises_external_service_error(self):
        _mock_rag.retrieval_query.side_effect = Exception("Service down")
        from app.core.exceptions import ExternalServiceError

        adapter = _make_adapter()
        with pytest.raises(ExternalServiceError, match="RAG Engine retrieval failed"):
            adapter.retrieve(query_text="test", top_k=5)

        _mock_rag.retrieval_query.side_effect = None

    def test_distance_threshold_passed(self):
        _mock_rag.retrieval_query.reset_mock()
        adapter = _make_adapter(rag_retrieval_distance_threshold=0.42)
        adapter.retrieve(query_text="test query", top_k=5)

        call_kwargs = _mock_rag.retrieval_query.call_args.kwargs
        config = call_kwargs.get("rag_retrieval_config")
        assert config is not None
        _mock_rag.Filter.assert_called()
        assert _mock_rag.Filter.call_args.kwargs.get("vector_distance_threshold") == 0.42


class TestDeleteFile:
    def test_delete_file_calls_rag_delete(self):
        _mock_rag.delete_file.reset_mock()
        adapter = _make_adapter()
        adapter.delete_file("projects/.../ragFiles/456")
        _mock_rag.delete_file.assert_called_once_with(name="projects/.../ragFiles/456")

    def test_delete_file_not_found_is_idempotent(self):
        from google.api_core import exceptions as gcp_exceptions
        _mock_rag.delete_file.side_effect = gcp_exceptions.NotFound("gone")

        adapter = _make_adapter()
        adapter.delete_file("projects/.../ragFiles/456")  # should not raise

        _mock_rag.delete_file.side_effect = None

    def test_delete_file_raises_on_other_errors(self):
        from app.core.exceptions import ExternalServiceError
        _mock_rag.delete_file.side_effect = Exception("Permission denied")

        adapter = _make_adapter()
        with pytest.raises(ExternalServiceError, match="Permission denied"):
            adapter.delete_file("projects/.../ragFiles/456")

        _mock_rag.delete_file.side_effect = None


class TestUriConversion:
    def test_gcs_to_gs(self):
        adapter = _make_adapter()
        assert adapter._to_gs_uri("gcs://bucket/key") == "gs://bucket/key"

    def test_gs_preserved(self):
        adapter = _make_adapter()
        assert adapter._to_gs_uri("gs://bucket/key") == "gs://bucket/key"


class TestFindRagFilePagination:
    def test_iterates_all_listed_files(self):
        mock_file_2 = MagicMock()
        mock_file_2.name = "projects/.../ragFiles/999"
        mock_file_2.source_uri = "gs://test-bucket/other.pdf"
        mock_file_match = MagicMock()
        mock_file_match.name = "projects/.../ragFiles/888"
        mock_file_match.source_uri = "gs://test-bucket/target.pdf"

        _mock_rag.list_files.return_value = [_mock_file, mock_file_2, mock_file_match]
        adapter = _make_adapter()
        result = adapter._find_rag_file_by_uri(
            corpus="projects/.../ragCorpora/123",
            gcs_uri="gs://test-bucket/target.pdf",
        )
        assert result == "projects/.../ragFiles/888"
        _mock_rag.list_files.return_value = [_mock_file]


class TestExtractFileId:
    def test_extracts_numeric_id(self):
        adapter = _make_adapter()
        assert adapter._extract_file_id("projects/p/l/ragCorpora/123/ragFiles/456") == "456"

    def test_trailing_slash(self):
        adapter = _make_adapter()
        assert adapter._extract_file_id("projects/p/l/ragCorpora/123/ragFiles/789/") == "789"
