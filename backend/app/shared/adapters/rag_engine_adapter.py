"""Vertex AI RAG Engine adapter.

Implements the ``IRagEngine`` port using the fully managed RAG Engine service.

Architecture
------------
RAG Engine handles parsing, chunking, embedding generation, and vector
indexing server-side via a single ``ImportRagFiles`` API call, and embeds
queries server-side for retrieval.  This adapter is a thin wrapper over the
``vertexai.preview.rag`` SDK — it holds **no database access**; the
document ↔ RAG-file mapping is managed by the ``rag`` module's application
layer inside the caller's transaction.

Deployment mode
---------------
The project targets **Serverless mode** with the
``RagManagedVertexVectorSearch`` (Vector Search 2.0) backend — the
recommended fully managed option.  Serverless mode is a one-time,
project-level configuration applied via ``scripts/setup_rag_engine.py``
and is **only available in ``us-central1``** — the adapter validates the
resolved location at first use and raises ``ConfigurationError`` otherwise.

Corpus management
-----------------
Prefer configuring ``RAG_CORPUS_RESOURCE`` explicitly (created via
``scripts/setup_rag_engine.py``).  When left empty the adapter auto-creates a
corpus on first use with the display name ``{APP_NAME}-{ENVIRONMENT}``, the
``RagManagedVertexVectorSearch`` backend, and the embedding model from
``RAG_EMBEDDING_MODEL`` (``text-embedding-005``).  Backend and embedding
model are **immutable** for the lifetime of a corpus.

Parsing
-------
- **Document AI Layout Parser** — used when ``RAG_LAYOUT_PARSER_ENABLED=True``
  (requires ``RAG_LAYOUT_PARSER_PROCESSOR_NAME``).  Produces context-aware
  chunks; recommended chunking is size 1024 / overlap 256.
  Note: files imported *without* the layout parser are not re-imported when
  it is later enabled — the RAG file must be deleted first (the ingestion
  service handles this on force re-ingest).
- **LLM Parser** — used when ``RAG_LLM_PARSER_MODEL`` is set (mutually
  exclusive with the layout parser).

Error semantics
---------------
All SDK failures raise ``ExternalServiceError`` — including partial import
failures (``failed_rag_files_count > 0``) — so callers can distinguish a
service outage from an empty result.  ``delete_file`` treats ``NotFound`` as
success (idempotent retries).

See: https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine
"""

from __future__ import annotations

import logging
import threading
import uuid as uuid_lib
from typing import Any

from app.core.config import Settings, get_settings
from app.core.exceptions import ConfigurationError, ExternalServiceError
from app.shared.interfaces import IRagEngine, RagIngestResult, RetrievedChunk

logger = logging.getLogger(__name__)

# Serverless mode is only available in us-central1.
_SERVERLESS_ALLOWED_LOCATIONS = frozenset({"us-central1"})


class RagEngineAdapter(IRagEngine):
    """RAG Engine adapter backed by ``vertexai.preview.rag``."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._corpus_name: str | None = None
        self._sdk_ready: bool = False
        self._corpus_lock = threading.Lock()

    @property
    def corpus_name(self) -> str:
        """The resolved corpus resource name (lazy-initialised on first use)."""
        return self._get_or_create_corpus()

    # ------------------------------------------------------------------
    # IRagEngine — ingest_file
    # ------------------------------------------------------------------

    def ingest_file(
        self,
        document_id: str,
        gcs_uri: str,
        display_name: str | None = None,
    ) -> RagIngestResult:
        """Import one Cloud Storage file into the RAG corpus.

        Chunking, parsing, and embedding all happen server-side according to
        the corpus and transformation configuration.  *display_name* is
        accepted for interface completeness but ``import_files`` derives the
        RAG file display name from the GCS object name.
        """
        gcs_uri = self._to_gs_uri(gcs_uri)
        corpus = self._get_or_create_corpus()

        logger.info(
            "rag_engine_import_start",
            extra={"document_id": document_id, "gcs_uri": gcs_uri, "corpus": corpus},
        )

        from vertexai.preview import rag  # noqa: PLC0415

        layout_parser = self._build_layout_parser(rag)
        llm_parser = self._build_llm_parser(rag)

        # The SDK forbids both parsers at once.
        if layout_parser is not None and llm_parser is not None:
            raise ConfigurationError(
                "Only one of RAG_LAYOUT_PARSER_ENABLED or "
                "RAG_LLM_PARSER_MODEL can be configured at a time."
            )

        import_kwargs: dict[str, Any] = {
            "corpus_name": corpus,
            "paths": [gcs_uri],
            "transformation_config": rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(
                    chunk_size=self.settings.rag_chunk_size,
                    chunk_overlap=self.settings.rag_chunk_overlap,
                ),
            ),
            "max_embedding_requests_per_min": (
                self.settings.rag_max_embedding_requests_per_min
            ),
            "timeout": self.settings.rag_import_timeout_seconds,
        }

        # The import API requires the sink object to NOT already exist, so a
        # unique object name is derived per import from the configured prefix.
        if self.settings.rag_import_result_sink:
            prefix = self.settings.rag_import_result_sink.rstrip("/")
            import_kwargs["import_result_sink"] = (
                f"{prefix}/{document_id}-{uuid_lib.uuid4().hex}.ndjson"
            )

        if layout_parser is not None:
            import_kwargs["layout_parser"] = layout_parser
        if llm_parser is not None:
            import_kwargs["llm_parser"] = llm_parser

        try:
            response = rag.import_files(**import_kwargs)
        except Exception as exc:
            logger.error(
                "rag_engine_import_failed",
                extra={"document_id": document_id, "error": str(exc)},
            )
            raise ExternalServiceError(
                f"RAG Engine import failed for document {document_id}: {exc}"
            ) from exc

        imported_count = int(getattr(response, "imported_rag_files_count", 0) or 0)
        skipped_count = int(getattr(response, "skipped_rag_files_count", 0) or 0)
        failed_count = int(getattr(response, "failed_rag_files_count", 0) or 0)

        if failed_count > 0:
            sink = import_kwargs.get("import_result_sink")
            raise ExternalServiceError(
                f"RAG Engine reported {failed_count} failed file(s) for "
                f"document {document_id} (source: {gcs_uri})."
                + (f" Details: {sink}" if sink else "")
            )

        # Discover the server-generated RAG file for this GCS object.  A
        # skipped import (hash-based dedup: same content + chunking config)
        # still has an existing RAG file with this source URI.
        rag_file_resource = self._find_rag_file_by_uri(corpus, gcs_uri)
        if rag_file_resource is None:
            raise ExternalServiceError(
                f"RAG Engine import completed but the RAG file for document "
                f"{document_id} (source: {gcs_uri}) could not be located in "
                f"the corpus."
            )

        rag_file_id = self._extract_file_id(rag_file_resource)

        logger.info(
            "rag_engine_import_complete",
            extra={
                "document_id": document_id,
                "rag_file_id": rag_file_id,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
            },
        )
        return RagIngestResult(
            rag_file_id=rag_file_id,
            rag_file_resource=rag_file_resource,
            imported_count=imported_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
        )

    # ------------------------------------------------------------------
    # IRagEngine — retrieve
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query_text: str,
        top_k: int = 5,
        rag_file_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """Text-based semantic search against the RAG corpus.

        The query is embedded server-side using the corpus's configured
        embedding model.  A ``vector_distance_threshold`` filters out
        low-quality matches (``RAG_RETRIEVAL_DISTANCE_THRESHOLD``).

        Raises ``ExternalServiceError`` on SDK failure so callers can
        distinguish an outage from an empty result.
        """
        if rag_file_ids is not None and not rag_file_ids:
            # An empty scope must be handled by the caller (return nothing);
            # passing it through would silently search the WHOLE corpus.
            raise ValueError("rag_file_ids must be None or non-empty")

        corpus = self._get_or_create_corpus()

        from vertexai.preview import rag  # noqa: PLC0415

        threshold = self.settings.rag_retrieval_distance_threshold

        try:
            response = rag.retrieval_query(
                text=query_text,
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=corpus,
                        rag_file_ids=rag_file_ids,
                    )
                ],
                rag_retrieval_config=rag.RagRetrievalConfig(
                    top_k=top_k,
                    filter=rag.Filter(vector_distance_threshold=threshold),
                ),
            )
        except Exception as exc:
            logger.error(
                "rag_engine_retrieval_failed",
                extra={
                    "query": query_text[:200],
                    "error": str(exc),
                    "threshold": threshold,
                },
            )
            raise ExternalServiceError(
                f"RAG Engine retrieval failed: {exc}"
            ) from exc

        return self._parse_retrieval_response(response)

    # ------------------------------------------------------------------
    # IRagEngine — delete_file
    # ------------------------------------------------------------------

    def delete_file(self, rag_file_resource: str) -> None:
        """Delete a RAG file from the corpus by its full resource name.

        Idempotent: a ``NotFound`` from the API means the file is already
        gone and is treated as success.
        """
        self._get_or_create_corpus()  # ensures SDK init + location check

        from google.api_core import exceptions as gcp_exceptions  # noqa: PLC0415
        from vertexai.preview import rag  # noqa: PLC0415

        try:
            rag.delete_file(name=rag_file_resource)
        except gcp_exceptions.NotFound:
            logger.info(
                "rag_engine_delete_already_gone",
                extra={"rag_file_resource": rag_file_resource},
            )
            return
        except Exception as exc:
            logger.error(
                "rag_engine_delete_failed",
                extra={"rag_file_resource": rag_file_resource, "error": str(exc)},
            )
            raise ExternalServiceError(
                f"RAG Engine delete failed for {rag_file_resource}: {exc}"
            ) from exc

        logger.info(
            "rag_engine_delete_complete",
            extra={"rag_file_resource": rag_file_resource},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_sdk(self) -> None:
        """Initialise the Vertex AI SDK once per adapter instance."""
        if self._sdk_ready:
            return
        import vertexai  # noqa: PLC0415

        vertexai.init(
            project=self.settings.gcp_project_id,
            location=self.settings.resolved_rag_engine_location,
        )
        self._sdk_ready = True

    def _get_or_create_corpus(self) -> str:
        """Return the corpus resource name, auto-creating if necessary.

        On first call validates the resolved location and — when no
        ``RAG_CORPUS_RESOURCE`` is configured — creates a corpus with the
        ``RagManagedVertexVectorSearch`` backend and the configured embedding
        model (both immutable after creation).
        """
        if self._corpus_name is not None:
            return self._corpus_name

        with self._corpus_lock:
            if self._corpus_name is not None:
                return self._corpus_name

            resolved_location = self.settings.resolved_rag_engine_location
            self._validate_location(resolved_location)

            self._ensure_sdk()

            if self.settings.rag_corpus_resource:
                self._corpus_name = self.settings.rag_corpus_resource
                logger.debug(
                    "rag_engine_using_configured_corpus",
                    extra={"corpus": self._corpus_name},
                )
                return self._corpus_name

            from vertexai.preview import rag  # noqa: PLC0415

            display_name = f"{self.settings.app_name}-{self.settings.environment}"
            logger.info(
                "rag_engine_creating_corpus",
                extra={
                    "display_name": display_name,
                    "location": resolved_location,
                    "embedding_model": self.settings.rag_embedding_model,
                },
            )

            # NOTE: the preview SDK's set_backend_config() feeds
            # backend_config.rag_embedding_model_config into a helper that
            # reads .publisher_model / .endpoint — i.e. it expects the
            # EmbeddingModelConfig shape, NOT RagEmbeddingModelConfig
            # (whose vertex_prediction_endpoint field crashes it).
            backend_config = rag.RagVectorDbConfig(
                vector_db=rag.RagManagedVertexVectorSearch(),
                rag_embedding_model_config=rag.EmbeddingModelConfig(
                    publisher_model=(
                        "publishers/google/models/"
                        f"{self.settings.rag_embedding_model}"
                    )
                ),
            )

            try:
                rag_corpus = rag.create_corpus(
                    display_name=display_name,
                    backend_config=backend_config,
                )
            except Exception as exc:
                raise ExternalServiceError(
                    f"Failed to auto-create RAG corpus '{display_name}' "
                    f"in {resolved_location}: {exc}"
                ) from exc

            self._corpus_name = rag_corpus.name
            logger.info(
                "rag_engine_corpus_created",
                extra={
                    "corpus": self._corpus_name,
                    "embedding_model": self.settings.rag_embedding_model,
                },
            )
            return self._corpus_name

    @staticmethod
    def _validate_location(location: str) -> None:
        """Validate that *location* supports serverless mode (us-central1 only)."""
        if location not in _SERVERLESS_ALLOWED_LOCATIONS:
            raise ConfigurationError(
                f"RAG Engine serverless mode requires location='us-central1'. "
                f"Resolved location: '{location}'. "
                "Set RAG_ENGINE_LOCATION=us-central1 (or "
                "GCP_LOCATION=us-central1) for serverless mode."
            )

    # -- Parser builders ------------------------------------------------------

    def _build_layout_parser(self, rag: Any) -> Any:
        """Build a LayoutParserConfig if enabled, else None."""
        if not self.settings.rag_layout_parser_enabled:
            return None
        processor_name = self.settings.rag_layout_parser_processor_name
        if not processor_name:
            raise ConfigurationError(
                "RAG_LAYOUT_PARSER_ENABLED is set but "
                "RAG_LAYOUT_PARSER_PROCESSOR_NAME is not configured. "
                "Create a Document AI Layout Parser processor in the "
                "Cloud Console and set the environment variable."
            )
        return rag.LayoutParserConfig(
            processor_name=processor_name,
            max_parsing_requests_per_min=(
                self.settings.rag_layout_parser_max_parsing_rpm
            ),
        )

    def _build_llm_parser(self, rag: Any) -> Any:
        """Build an LlmParserConfig if a model is configured, else None."""
        if not self.settings.rag_llm_parser_model:
            return None
        return rag.LlmParserConfig(
            model_name=self.settings.rag_llm_parser_model,
        )

    # -- URI helpers ---------------------------------------------------------

    @staticmethod
    def _to_gs_uri(uri: str) -> str:
        """Convert ``gcs://bucket/key`` → ``gs://bucket/key``."""
        if uri.startswith("gcs://"):
            return "gs://" + uri[6:]
        if uri.startswith("gs://"):
            return uri
        return f"gs://{uri}"

    @staticmethod
    def _extract_file_id(rag_file_resource: str) -> str:
        """Extract the file ID from a RAG file resource name.

        ``projects/{p}/locations/{l}/ragCorpora/{c}/ragFiles/{id}`` → ``{id}``
        """
        return rag_file_resource.rstrip("/").rsplit("/", 1)[-1]

    # -- RAG file discovery --------------------------------------------------

    def _find_rag_file_by_uri(self, corpus: str, gcs_uri: str) -> str | None:
        """Find the RAG file resource name for *gcs_uri* in *corpus*.

        Iterates lazily through the corpus files and returns on first match.
        Returns ``None`` when no match is found.
        """
        from vertexai.preview import rag  # noqa: PLC0415

        try:
            for f in rag.list_files(corpus_name=corpus):
                file_uri = getattr(f, "source_uri", None) or getattr(
                    f, "display_name", ""
                )
                if file_uri == gcs_uri:
                    return f.name
        except Exception as exc:
            logger.warning(
                "rag_engine_list_files_failed",
                extra={"corpus": corpus, "error": str(exc)},
            )
        return None

    # -- Response parsing ----------------------------------------------------

    @staticmethod
    def _parse_retrieval_response(response: Any) -> list[RetrievedChunk]:
        """Parse a ``retrieval_query`` response into ``RetrievedChunk`` items."""
        results: list[RetrievedChunk] = []

        contexts = getattr(response, "contexts", None)
        if contexts is None:
            return results

        context_list = getattr(contexts, "contexts", None)
        if context_list is None:
            return results

        for ctx in context_list:
            text = getattr(ctx, "text", "") or ""
            source_uri = getattr(ctx, "source_uri", "") or ""

            # The v1beta1 Context exposes the retrieval metric as the optional
            # ``score`` field (COSINE_DISTANCE for the managed backend: 0 =
            # most relevant, 2 = least).  Older responses populate ``distance``
            # instead — fall back to it when ``score`` is unset.
            distance = getattr(ctx, "score", None)
            if distance is None:
                distance = getattr(ctx, "distance", None)

            # The RAG chunk's ``file_id`` is the numeric RAG file ID.  We
            # extract it here so the retrieval service can reverse-map
            # documents for title enrichment.
            chunk = getattr(ctx, "chunk", None)
            rag_file_id: str | None = None
            if chunk is not None:
                rag_file_id = getattr(chunk, "file_id", None) or None

            # Convert cosine distance (lower = more similar) to a 0–1
            # similarity score for consumers.
            score: float | None = None
            if distance is not None:
                try:
                    distance = float(distance)
                    score = round(max(0.0, min(1.0, 1.0 - distance)), 6)
                except (TypeError, ValueError):
                    distance = None

            results.append(
                RetrievedChunk(
                    text=text,
                    source_uri=source_uri,
                    rag_file_id=rag_file_id,
                    score=score,
                    distance=distance,
                )
            )

        return results
