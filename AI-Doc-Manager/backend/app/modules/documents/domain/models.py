import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.shared.enums import DocumentType, Status, enum_values

document_type_enum = Enum(
    DocumentType,
    name="document_type_enum",
    values_callable=enum_values,
)
status_enum = Enum(
    Status,
    name="status_enum",
    values_callable=enum_values,
)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("document_group_id", "version", name="uq_documents_group_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_group_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(document_type_enum, nullable=False)
    status: Mapped[Status] = mapped_column(status_enum, nullable=False)
    file_link: Mapped[str] = mapped_column(String(500), nullable=False)
    is_vectorized: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    modified_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    modified_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    rejected_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    rejected_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )

    creator: Mapped["User | None"] = relationship(
        back_populates="created_documents",
        foreign_keys=[created_by],
    )
    modifier: Mapped["User | None"] = relationship(
        back_populates="modified_documents",
        foreign_keys=[modified_by],
    )
    reviews: Mapped[list["DocumentReview"]] = relationship(back_populates="document")
