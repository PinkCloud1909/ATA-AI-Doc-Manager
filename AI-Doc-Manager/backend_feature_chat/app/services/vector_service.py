"""
services/vector_service.py
Wrapper cho Vertex AI Vector Search (Matching Engine).

Luồng:
  1. Khi Document được APPROVED → embed nội dung → upsert vào Vector Index
  2. Khi Chat nhận query → embed query → find_neighbors → trả về SourceReferences
  3. Khi Document EXPIRED  → remove khỏi Vector Index
"""
from __future__ import annotations

import json
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform

from app.core.config import settings
from app.schemas.chat import SourceReference

logger = structlog.get_logger()

# ── Embedding model ───────────────────────────────────────────────────────────
_EMBEDDING_MODEL = "text-multilingual-embedding-002"  # hỗ trợ tiếng Việt

# ── Lazy singletons ───────────────────────────────────────────────────────────
_embedding_model: TextEmbeddingModel | None = None
_index_endpoint: aiplatform.MatchingEngineIndexEndpoint | None = None


def _get_embedding_model() -> TextEmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.VERTEX_AI_LOCATION)
        _embedding_model = TextEmbeddingModel.from_pretrained(_EMBEDDING_MODEL)
    return _embedding_model


def _get_index_endpoint() -> aiplatform.MatchingEngineIndexEndpoint:
    global _index_endpoint
    if _index_endpoint is None:
        aiplatform.init(project=settings.GCP_PROJECT_ID, location=settings.VERTEX_AI_LOCATION)
        _index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=settings.VECTOR_SEARCH_INDEX_ENDPOINT
        )
    return _index_endpoint


# ── Public API ────────────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def embed_text(text: str) -> list[float]:
    """
    Tạo embedding vector cho một đoạn text.
    Dùng text-multilingual-embedding-002 để hỗ trợ tiếng Việt.
    """
    model = _get_embedding_model()
    embeddings = model.get_embeddings([text])
    return embeddings[0].values


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def upsert_document(
    document_id: str,
    text_content: str,
    metadata: dict,
) -> None:
    """
    Embed document content và upsert vào Vertex AI Vector Index.
    Gọi khi Document status chuyển sang APPROVED.

    metadata: {
        document_group_id, version, original_filename,
        gcs_path, document_type
    }
    """
    logger.info("vector_upsert_start", document_id=document_id)

    # Chunk text nếu dài (Vertex AI giới hạn token per embedding)
    chunks = _chunk_text(text_content, max_chars=2000)
    vectors = []

    for i, chunk in enumerate(chunks):
        embedding = await embed_text(chunk)
        chunk_id = f"{document_id}_chunk_{i}"
        vectors.append({
            "id":         chunk_id,
            "embedding":  embedding,
            "restricts":  [
                {"namespace": "status",  "allow_list": ["APPROVED"]},
                {"namespace": "doc_id",  "allow_list": [document_id]},
            ],
            "crowding_tag": {"value": document_id},  # 1 doc không dominate kết quả
        })

    # Upsert vào index (batch)
    endpoint = _get_index_endpoint()
    # NOTE: Vertex AI Vector Search upsert qua Index (không phải Endpoint)
    # Trong production dùng aiplatform.MatchingEngineIndex.upsert_datapoints()
    index = aiplatform.MatchingEngineIndex(
        index_name=settings.VECTOR_SEARCH_INDEX_ID
    )
    index.upsert_datapoints(
        datapoints=[
            aiplatform.gapic.IndexDatapoint(
                datapoint_id=v["id"],
                feature_vector=v["embedding"],
                restricts=[
                    aiplatform.gapic.IndexDatapoint.Restriction(
                        namespace=r["namespace"],
                        allow_list=r["allow_list"],
                    )
                    for r in v["restricts"]
                ],
                crowding_tag=aiplatform.gapic.IndexDatapoint.CrowdingTag(
                    crowding_attribute=v["crowding_tag"]["value"]
                ),
            )
            for v in vectors
        ]
    )

    logger.info("vector_upsert_done", document_id=document_id, chunks=len(chunks))


async def remove_document(document_id: str) -> None:
    """
    Xóa document khỏi Vector Index khi status → EXPIRED.
    """
    logger.info("vector_remove", document_id=document_id)
    index = aiplatform.MatchingEngineIndex(index_name=settings.VECTOR_SEARCH_INDEX_ID)
    # Xóa tất cả chunks của document
    # Trong thực tế cần track chunk count; ở đây xóa theo prefix pattern
    # Vertex AI không hỗ trợ wildcard → cần lưu chunk_ids trong PostgreSQL
    # (Simplified version — production cần store chunk_ids)
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def search_approved_documents(
    query: str,
    top_k: int | None = None,
    document_metadata: dict | None = None,  # {doc_id: {group_id, version, ...}}
) -> list[SourceReference]:
    """
    Semantic search trong Vector Index, chỉ lấy docs APPROVED.
    Trả về list[SourceReference] với relevance_score.

    document_metadata: lookup dict từ PostgreSQL (doc_id → metadata)
    """
    k = top_k or settings.VECTOR_SEARCH_TOP_K
    logger.info("vector_search_start", query_len=len(query), top_k=k)

    query_embedding = await embed_text(query)

    endpoint = _get_index_endpoint()
    response = endpoint.find_neighbors(
        deployed_index_id=settings.VECTOR_SEARCH_INDEX_ENDPOINT.split("/")[-1],
        queries=[query_embedding],
        num_neighbors=k * 3,    # lấy nhiều hơn để dedupe theo document
        filter=[
            aiplatform.gapic.IndexDatapoint.Restriction(
                namespace="status",
                allow_list=["APPROVED"],
            )
        ],
    )

    if not response or not response[0]:
        logger.info("vector_search_no_results")
        return []

    # Dedupe: mỗi document chỉ lấy chunk có score cao nhất
    best_per_doc: dict[str, dict] = {}
    for neighbor in response[0]:
        # chunk_id format: "{document_id}_chunk_{n}"
        doc_id = "_".join(neighbor.id.split("_")[:-2])
        distance = neighbor.distance  # cosine distance (0 = identical, 2 = opposite)

        if doc_id not in best_per_doc or distance < best_per_doc[doc_id]["distance"]:
            best_per_doc[doc_id] = {"distance": distance, "chunk_id": neighbor.id}

    # Filter theo threshold và build SourceReferences
    sources: list[SourceReference] = []
    threshold = settings.VECTOR_SEARCH_DISTANCE_THRESHOLD

    for doc_id, hit in sorted(best_per_doc.items(), key=lambda x: x[1]["distance"]):
        if hit["distance"] > threshold:
            continue

        meta = (document_metadata or {}).get(doc_id, {})
        relevance = max(0.0, round(1.0 - hit["distance"] / 2.0, 3))  # normalize to 0-1

        sources.append(SourceReference(
            document_id=doc_id,
            document_group_id=meta.get("document_group_id", ""),
            version=meta.get("version", 0),
            original_filename=meta.get("original_filename", ""),
            gcs_path=meta.get("gcs_path", ""),
            vertex_distance=round(hit["distance"], 4),
            relevance_score=relevance,
        ))

        if len(sources) >= k:
            break

    logger.info("vector_search_done", results=len(sources))
    return sources


# ── Helpers ───────────────────────────────────────────────────────────────────

def _chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    """Chia text thành chunks theo paragraph, tối đa max_chars mỗi chunk."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            current = para[:max_chars]   # hard truncate nếu 1 para quá dài

    if current:
        chunks.append(current)

    return chunks or [text[:max_chars]]
