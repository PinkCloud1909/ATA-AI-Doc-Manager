"""
services/chat_service.py
Orchestrator cho toàn bộ Chat AI flow.

Flow chính:
  1. Embed query → Vertex AI Vector Search → lấy approved docs
  2. Fetch document content từ GCS
  3. Gọi Gemini (RAG hoặc fallback)
  4. Lưu ChatMessage vào PostgreSQL
  5. Trả về ChatResponse (REST) hoặc stream tokens (WebSocket)
"""
from __future__ import annotations

import uuid
import structlog
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app import models
from app.schemas.chat import (
    ChatRequest, ChatResponse, SourceReference,
    WsTokenMessage, WsSourcesMessage, WsDoneMessage, WsErrorMessage,
)
from app.services import vector_service, gemini_service, gcs_service

logger = structlog.get_logger()


# ── Session management ────────────────────────────────────────────────────────

async def get_or_create_session(
    session_id_str: str,
    user: models.User,
    db: AsyncSession,
) -> models.ChatSession:
    """
    Tìm session theo ID (từ FE chatStore.sessionId).
    Nếu chưa tồn tại → tạo mới.
    """
    try:
        session_uuid = uuid.UUID(session_id_str)
    except ValueError:
        session_uuid = uuid.uuid4()

    result = await db.execute(
        select(models.ChatSession).where(models.ChatSession.id == session_uuid)
    )
    session = result.scalar_one_or_none()

    if session is None:
        session = models.ChatSession(id=session_uuid, user_id=user.id)
        db.add(session)
        await db.flush()

    return session


async def get_conversation_history(
    session: models.ChatSession,
    max_turns: int | None = None,
) -> list[dict]:
    """Lấy lịch sử hội thoại dạng list[{role, content}] để truyền vào Gemini."""
    limit = (max_turns or settings.CHAT_MAX_HISTORY_TURNS) * 2
    messages = session.messages[-limit:] if session.messages else []
    return [{"role": m.role.value, "content": m.content} for m in messages]


async def _fetch_source_contents(sources: list[SourceReference]) -> dict[str, str]:
    """
    Fetch nội dung text từ GCS cho các documents được tìm thấy.
    Chạy sequential (Vertex AI quota) — có thể optimize thành asyncio.gather.
    """
    contents: dict[str, str] = {}
    for source in sources:
        try:
            text = await gcs_service.fetch_document_text(source.gcs_path)
            contents[source.document_id] = text
        except Exception as e:
            logger.warning("gcs_fetch_failed", doc_id=source.document_id, error=str(e))
            contents[source.document_id] = ""
    return contents


async def _fetch_doc_metadata(
    doc_ids: list[str],
    db: AsyncSession,
) -> dict[str, dict]:
    """
    Tra cứu metadata của documents từ PostgreSQL để enrich SourceReference.
    """
    if not doc_ids:
        return {}

    uuids = []
    for did in doc_ids:
        try:
            uuids.append(uuid.UUID(did))
        except ValueError:
            pass

    result = await db.execute(
        select(models.Document).where(models.Document.id.in_(uuids))
    )
    docs = result.scalars().all()

    return {
        str(d.id): {
            "document_group_id": str(d.document_group_id),
            "version":           d.version,
            "original_filename": d.original_filename,
            "gcs_path":          d.gcs_path,
            "document_type":     d.document_type.value,
        }
        for d in docs
    }


async def _save_messages(
    session: models.ChatSession,
    user_message: str,
    assistant_message: str,
    sources: list[SourceReference],
    is_from_kb: bool,
    model_used: str,
    db: AsyncSession,
) -> models.ChatMessage:
    """Lưu cặp user/assistant message vào DB. Trả về assistant message."""

    # User message
    db.add(models.ChatMessage(
        session_id=session.id,
        role=models.MessageRole.USER,
        content=user_message,
    ))

    # Assistant message
    assistant = models.ChatMessage(
        session_id=session.id,
        role=models.MessageRole.ASSISTANT,
        content=assistant_message,
        is_from_kb=is_from_kb,
        model_used=model_used,
        sources=[s.model_dump() for s in sources],
    )
    db.add(assistant)

    # Auto-generate session title từ first message
    if not session.title:
        session.title = await gemini_service.generate_title(user_message)

    await db.flush()
    return assistant


# ── REST handler ──────────────────────────────────────────────────────────────

async def handle_chat(
    request: ChatRequest,
    user: models.User,
    db: AsyncSession,
) -> ChatResponse:
    """
    Non-streaming handler cho POST /chat.
    Dùng khi FE không dùng WebSocket (fallback hoặc Flutter).
    """
    logger.info("chat_start", user_id=str(user.id), session_id=request.session_id)

    session  = await get_or_create_session(request.session_id, user, db)
    history  = await get_conversation_history(session)

    # 1. Vector search
    doc_metadata = {}
    sources = await vector_service.search_approved_documents(
        query=request.message,
        document_metadata={},  # enriched below
    )

    # 2. Enrich sources với metadata từ PostgreSQL
    if sources:
        doc_ids   = [s.document_id for s in sources]
        doc_metadata = await _fetch_doc_metadata(doc_ids, db)
        for s in sources:
            meta = doc_metadata.get(s.document_id, {})
            s.document_group_id = meta.get("document_group_id", "")
            s.version           = meta.get("version", 0)
            s.original_filename = meta.get("original_filename", "")
            s.gcs_path          = meta.get("gcs_path", "")

    # 3. Fetch document contents từ GCS
    source_contents = await _fetch_source_contents(sources)

    # 4. Gemini generate
    answer, model_used = await gemini_service.generate_answer(
        query=request.message,
        sources=sources,
        source_contents=source_contents,
        conversation_history=history,
    )

    is_from_kb = bool(sources)

    # 5. Lưu messages
    assistant_msg = await _save_messages(
        session, request.message, answer,
        sources, is_from_kb, model_used, db,
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
        is_from_kb=is_from_kb,
        session_id=request.session_id,
        model_used=model_used,
        message_id=str(assistant_msg.id),
    )


# ── WebSocket streaming handler ───────────────────────────────────────────────

async def stream_chat(
    request: ChatRequest,
    user: models.User,
    db: AsyncSession,
) -> AsyncGenerator[dict, None]:
    """
    Streaming handler cho WebSocket /chat/ws/{session_id}.
    Yields dict messages để endpoint serialize thành JSON.

    Protocol (khớp với FE chatApi.createStreamingConnection):
      {"type": "token",   "content": "..."}  ← text chunk từ Gemini
      {"type": "sources", "sources": [...], "is_from_kb": bool}
      {"type": "done",    "message_id": "...", "model_used": "..."}
      {"type": "error",   "message": "..."}   ← nếu có lỗi
    """
    try:
        session = await get_or_create_session(request.session_id, user, db)
        history = await get_conversation_history(session)

        # 1. Vector search (trước khi stream để gửi sources sớm)
        sources: list[SourceReference] = await vector_service.search_approved_documents(
            query=request.message,
        )

        # 2. Enrich & fetch content
        if sources:
            doc_ids = [s.document_id for s in sources]
            doc_metadata = await _fetch_doc_metadata(doc_ids, db)
            for s in sources:
                meta = doc_metadata.get(s.document_id, {})
                s.document_group_id = meta.get("document_group_id", "")
                s.version           = meta.get("version", 0)
                s.original_filename = meta.get("original_filename", "")
                s.gcs_path          = meta.get("gcs_path", "")
                # Add signed download URL cho FE
                if s.gcs_path:
                    try:
                        s.download_url = gcs_service.generate_signed_download_url(s.gcs_path)
                    except Exception:
                        pass

        source_contents = await _fetch_source_contents(sources)

        # 3. Gửi sources trước khi stream tokens (FE hiển thị ngay)
        yield WsSourcesMessage(
            sources=sources,
            is_from_kb=bool(sources),
        ).model_dump()

        # 4. Stream tokens từ Gemini
        full_answer = ""
        model_used  = settings.GEMINI_MODEL

        async for token in gemini_service.stream_answer(
            query=request.message,
            sources=sources,
            source_contents=source_contents,
            conversation_history=history,
        ):
            full_answer += token
            yield WsTokenMessage(content=token).model_dump()

        # 5. Lưu vào DB sau khi stream xong
        assistant_msg = await _save_messages(
            session, request.message, full_answer,
            sources, bool(sources), model_used, db,
        )

        yield WsDoneMessage(
            message_id=str(assistant_msg.id),
            model_used=model_used,
        ).model_dump()

    except Exception as e:
        logger.error("chat_stream_error", error=str(e))
        yield WsErrorMessage(message="Đã xảy ra lỗi. Vui lòng thử lại.").model_dump()
