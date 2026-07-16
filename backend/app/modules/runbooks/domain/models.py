import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Runbook(Base):
    __tablename__ = "runbooks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)
    document_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="generating"
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )
    modified_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )

    creator: Mapped["User | None"] = relationship(
        foreign_keys=[created_by],
    )
