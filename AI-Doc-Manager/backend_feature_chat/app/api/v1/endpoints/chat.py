"""
api/v1/endpoints/chat.py
Hai endpoints cho Chat AI module:
  POST /chat          — REST (non-streaming), dùng cho Flutter / fallback
  WS   /chat/ws/{id} — WebSocket streaming, dùng cho Next.js ChatWindow.tsx
"""
from __future__ import annotations

import json
import structlog
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db, AsyncSessionLocal
from app import models
from app.schemas.chat import (
    ChatRequest, ChatResponse,
    ChatSessionRead, ChatHistoryResponse, ChatMessageRead,
)
from app.services import chat_service
from app.services.chat_service import get_or_create_session

# Firebase token verify (dùng lại logic từ security.py)
import firebase_admin
from firebase_admin import auth as firebase_auth

logger = structlog.get_logger()
router = APIRouter(prefix="/chat", tags=["Chat AI"])


# ── REST endpoint ─────────────────────────────────────────────────────────────

@router.post("", response_model=ChatResponse)
async def post_chat(
    request: ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Non-streaming chat.
    Dùng cho: Flutter mobile app, environments không hỗ trợ WebSocket.
    """
    return await chat_service.handle_chat(request, current_user, db)


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(..., description="Firebase ID Token"),
):
    """
    WebSocket streaming endpoint.
    FE gửi token qua query param vì WS không hỗ trợ Authorization header.

    Khớp với chatApi.createStreamingConnection() trong lib/api/chat.ts:
      new WebSocket(`${WS_BASE}/chat/ws/${sessionId}?token=${idToken}`)
    """
    await websocket.accept()

    # ── Authenticate ─────────────────────────────────────────────────────────
    user: models.User | None = None
    async with AsyncSessionLocal() as db:
        try:
            decoded      = firebase_auth.verify_id_token(token)
            firebase_uid = decoded["uid"]

            result = await db.execute(
                select(models.User).where(models.User.firebase_uid == firebase_uid)
            )
            user = result.scalar_one_or_none()

            if user is None:
                await websocket.send_json({"type": "error", "message": "Unauthorized"})
                await websocket.close(code=1008)
                return

        except Exception:
            await websocket.send_json({"type": "error", "message": "Token không hợp lệ"})
            await websocket.close(code=1008)
            return

    logger.info("ws_connected", user_id=str(user.id), session_id=session_id)

    # ── Message loop ─────────────────────────────────────────────────────────
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            request = ChatRequest(
                message=payload.get("message", ""),
                session_id=payload.get("session_id", session_id),
                mode=payload.get("mode", "text"),
            )

            # Stream response qua WebSocket
            async with AsyncSessionLocal() as db:
                async for ws_message in chat_service.stream_chat(request, user, db):
                    await websocket.send_json(ws_message)

    except WebSocketDisconnect:
        logger.info("ws_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("ws_error", error=str(e))
        try:
            await websocket.send_json({"type": "error", "message": "Lỗi kết nối"})
        except Exception:
            pass


# ── Session history ───────────────────────────────────────────────────────────

@router.get("/sessions", response_model=list[ChatSessionRead])
async def list_sessions(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy danh sách chat sessions của user.
    Dùng cho ChatSidebar.tsx — hiển thị lịch sử hội thoại.
    """
    result = await db.execute(
        select(models.ChatSession)
        .where(models.ChatSession.user_id == current_user.id)
        .order_by(models.ChatSession.updated_at.desc())
        .limit(50)
    )
    sessions = result.scalars().all()

    return [
        ChatSessionRead(
            id=str(s.id),
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(s.messages),
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lấy full history của một session.
    Dùng khi user click vào session cũ trong ChatSidebar.tsx.
    """
    import uuid as _uuid
    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session không tồn tại")

    result = await db.execute(
        select(models.ChatSession).where(
            models.ChatSession.id == sid,
            models.ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session không tồn tại")

    return ChatHistoryResponse(
        session=ChatSessionRead(
            id=str(session.id),
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=len(session.messages),
        ),
        messages=[
            ChatMessageRead(
                id=str(m.id),
                role=m.role.value,
                content=m.content,
                is_from_kb=m.is_from_kb,
                model_used=m.model_used,
                sources=[
                    # Rehydrate từ JSON stored
                    s if isinstance(s, dict) else s
                    for s in (m.sources or [])
                ],
                created_at=m.created_at,
            )
            for m in session.messages
        ],
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Xóa chat session và toàn bộ messages."""
    import uuid as _uuid
    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(models.ChatSession).where(
            models.ChatSession.id == sid,
            models.ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(session)
