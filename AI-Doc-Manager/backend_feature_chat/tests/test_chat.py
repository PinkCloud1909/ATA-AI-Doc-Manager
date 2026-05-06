"""
tests/test_chat.py
Unit tests cho chat module.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.chat import ChatRequest, SourceReference


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id          = "00000000-0000-0000-0000-000000000001"
    user.firebase_uid = "firebase_test_uid"
    user.username    = "testuser"
    user.email       = "test@example.com"
    user.user_roles  = []
    return user


@pytest.fixture
def mock_sources():
    return [
        SourceReference(
            document_id="doc-1",
            document_group_id="group-1",
            version=2,
            original_filename="deploy-guide.pdf",
            gcs_path="runbook-documents/group-1/v2/deploy-guide.pdf",
            vertex_distance=0.15,
            relevance_score=0.925,
        )
    ]


# ── Vector Service Tests ───────────────────────────────────────────────────────

class TestVectorService:

    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self):
        with patch("app.services.vector_service._get_embedding_model") as mock_model:
            mock_embedding = MagicMock()
            mock_embedding.values = [0.1] * 768
            mock_model.return_value.get_embeddings.return_value = [mock_embedding]

            from app.services.vector_service import embed_text
            result = await embed_text("Test query về deployment")

            assert len(result) == 768
            assert all(isinstance(v, float) for v in result)

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_no_results(self):
        with patch("app.services.vector_service.embed_text", return_value=[0.1] * 768), \
             patch("app.services.vector_service._get_index_endpoint") as mock_ep:
            mock_ep.return_value.find_neighbors.return_value = [[]]

            from app.services.vector_service import search_approved_documents
            results = await search_approved_documents("query không có kết quả")

            assert results == []

    def test_chunk_text_splits_correctly(self):
        from app.services.vector_service import _chunk_text
        long_text = "paragraph " * 500  # ~5000 chars
        chunks = _chunk_text(long_text, max_chars=2000)
        assert len(chunks) >= 2
        assert all(len(c) <= 2000 for c in chunks)


# ── Chat Service Tests ─────────────────────────────────────────────────────────

class TestChatService:

    @pytest.mark.asyncio
    async def test_handle_chat_with_sources(self, mock_user, mock_sources):
        mock_db = AsyncMock()

        with patch("app.services.chat_service.get_or_create_session") as mock_session, \
             patch("app.services.chat_service.vector_service.search_approved_documents",
                   return_value=mock_sources), \
             patch("app.services.chat_service._fetch_source_contents",
                   return_value={"doc-1": "Nội dung tài liệu về deployment..."}), \
             patch("app.services.chat_service._fetch_doc_metadata",
                   return_value={"doc-1": {"document_group_id": "group-1", "version": 2,
                                           "original_filename": "deploy-guide.pdf",
                                           "gcs_path": "bucket/path.pdf"}}), \
             patch("app.services.chat_service.gemini_service.generate_answer",
                   return_value=("Đây là hướng dẫn deployment từ tài liệu...", "gemini-1.5-pro")), \
             patch("app.services.chat_service._save_messages") as mock_save:

            mock_session.return_value.messages = []
            mock_session.return_value.title = None
            mock_save.return_value = MagicMock(id="msg-1")

            from app.services.chat_service import handle_chat
            request = ChatRequest(
                message="Hướng dẫn deploy lên Kubernetes?",
                session_id="00000000-0000-0000-0000-000000000002",
                mode="text",
            )

            response = await handle_chat(request, mock_user, mock_db)

            assert response.is_from_kb is True
            assert len(response.sources) == 1
            assert response.sources[0].original_filename == "deploy-guide.pdf"

    @pytest.mark.asyncio
    async def test_handle_chat_fallback_no_sources(self, mock_user):
        mock_db = AsyncMock()

        with patch("app.services.chat_service.get_or_create_session") as mock_session, \
             patch("app.services.chat_service.vector_service.search_approved_documents",
                   return_value=[]), \
             patch("app.services.chat_service.gemini_service.generate_answer",
                   return_value=("Tôi không tìm thấy tài liệu cụ thể, nhưng...", "gemini-1.5-pro")), \
             patch("app.services.chat_service._save_messages") as mock_save:

            mock_session.return_value.messages = []
            mock_session.return_value.title = None
            mock_save.return_value = MagicMock(id="msg-2")

            from app.services.chat_service import handle_chat
            request = ChatRequest(
                message="Cách config firewall AWS?",
                session_id="00000000-0000-0000-0000-000000000003",
                mode="text",
            )

            response = await handle_chat(request, mock_user, mock_db)

            assert response.is_from_kb is False
            assert response.sources == []


# ── API Integration Tests ─────────────────────────────────────────────────────

class TestChatAPI:

    @pytest.mark.asyncio
    async def test_post_chat_unauthorized(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/chat", json={
                "message": "test",
                "session_id": "00000000-0000-0000-0000-000000000001",
                "mode": "text",
            })
        assert response.status_code == 403   # No Bearer token

    @pytest.mark.asyncio
    async def test_health_check(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
