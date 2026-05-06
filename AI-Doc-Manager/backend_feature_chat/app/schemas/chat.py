"""
schemas/chat.py
Khớp 1-1 với src/types/chat.ts của FE.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


# ── Source Reference ──────────────────────────────────────────────────────────
class SourceReference(BaseModel):
    """Kết quả từ Vertex AI Vector Search — khớp với SourceReference trong chat.ts"""
    document_id:       str
    document_group_id: str
    version:           int
    original_filename: str
    gcs_path:          str
    download_url:      str | None = None

    # Vertex AI Vector Search scores
    vertex_distance:   float | None = None   # cosine distance (thấp = liên quan hơn)
    relevance_score:   float | None = None   # 1 - vertex_distance


# ── Chat Request / Response ───────────────────────────────────────────────────
class ChatRequest(BaseModel):
    """POST /chat và WebSocket payload từ FE"""
    message:    str = Field(..., min_length=1, max_length=8000)
    session_id: str = Field(..., description="UUID từ chatStore.sessionId")
    mode:       str = Field("text", pattern="^(text|voice)$")


class ChatResponse(BaseModel):
    """Response cho REST endpoint (non-streaming)"""
    answer:      str
    sources:     list[SourceReference] = []
    is_from_kb:  bool                  = False
    session_id:  str
    model_used:  str | None            = None
    message_id:  str                   = Field(default_factory=lambda: str(uuid.uuid4()))


# ── WebSocket stream messages ─────────────────────────────────────────────────
class WsTokenMessage(BaseModel):
    type:    str = "token"
    content: str


class WsSourcesMessage(BaseModel):
    type:       str = "sources"
    sources:    list[SourceReference]
    is_from_kb: bool


class WsDoneMessage(BaseModel):
    type:       str  = "done"
    message_id: str
    model_used: str | None = None


class WsErrorMessage(BaseModel):
    type:    str = "error"
    message: str


# ── Session CRUD ──────────────────────────────────────────────────────────────
class ChatSessionRead(BaseModel):
    id:         str
    title:      str | None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ChatMessageRead(BaseModel):
    id:         str
    role:       str
    content:    str
    is_from_kb: bool
    model_used: str | None
    sources:    list[SourceReference] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    session:  ChatSessionRead
    messages: list[ChatMessageRead]
