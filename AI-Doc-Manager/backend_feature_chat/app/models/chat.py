"""
models/chat.py
Lưu lịch sử hội thoại vào PostgreSQL để:
  - Hiển thị lại lịch sử khi user reload trang (ChatSidebar.tsx)
  - Dùng làm conversation context cho Gemini (multi-turn)
  - Audit log
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, Integer, Enum, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class MessageRole(str, enum.Enum):
    USER      = "user"
    ASSISTANT = "assistant"


class ChatSession(Base):
    """
    Một phiên hội thoại (1 session = 1 chuỗi hỏi-đáp liên tục).
    Tương ứng với sessionId trong chatStore.ts của FE.
    """
    __tablename__ = "chat_sessions"

    id:         Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:    Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title:      Mapped[str | None]= mapped_column(String(500))   # auto-generated từ turn đầu tiên
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user:     Mapped["User"]           = relationship(back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        order_by="ChatMessage.created_at",
        lazy="selectin",
    )


class ChatMessage(Base):
    """
    Một tin nhắn trong phiên hội thoại.
    sources lưu dạng JSON list — mỗi item là SourceReference từ Vertex AI.
    """
    __tablename__ = "chat_messages"

    id:         Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID]   = mapped_column(ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role:       Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content:    Mapped[str]         = mapped_column(Text, nullable=False)
    is_from_kb: Mapped[bool]        = mapped_column(Boolean, default=False)   # True = từ Vertex AI search
    model_used: Mapped[str | None]  = mapped_column(String(100))              # gemini-1.5-pro / gemini-1.5-flash
    sources:    Mapped[list | None] = mapped_column(JSON)                     # list[SourceReference]
    created_at: Mapped[datetime]    = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
