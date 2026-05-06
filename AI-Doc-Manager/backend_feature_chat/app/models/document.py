import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, Integer, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class DocumentStatus(str, enum.Enum):
    DRAFT          = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED       = "APPROVED"
    REJECTED       = "REJECTED"
    EXPIRED        = "EXPIRED"


class DocumentType(str, enum.Enum):
    TEMPLATE          = "TEMPLATE"
    CUSTOMER_SPECIFIC = "CUSTOMER_SPECIFIC"
    COMMON_GUIDE      = "COMMON_GUIDE"


class Document(Base):
    __tablename__ = "documents"

    id:                Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_group_id: Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    version:           Mapped[int]             = mapped_column(Integer, nullable=False, default=1)
    document_type:     Mapped[DocumentType]    = mapped_column(Enum(DocumentType), nullable=False)
    status:            Mapped[DocumentStatus]  = mapped_column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)

    # GCS fields
    gcs_path:          Mapped[str]             = mapped_column(String(1000), nullable=False)
    original_filename: Mapped[str]             = mapped_column(String(500), nullable=False)
    content_type:      Mapped[str]             = mapped_column(String(100), nullable=False)
    size_bytes:        Mapped[int | None]      = mapped_column(Integer)

    # Vertex AI Vector Search
    is_vectorized:     Mapped[bool]            = mapped_column(Boolean, default=False)
    vertex_index_id:   Mapped[str | None]      = mapped_column(String(500))

    created_by:    Mapped[uuid.UUID]        = mapped_column(ForeignKey("users.id"), nullable=False)
    modified_by:   Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at:    Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_date: Mapped[datetime | None]  = mapped_column(DateTime(timezone=True), onupdate=func.now())

    reviews: Mapped[list["DocumentReview"]] = relationship(back_populates="document", lazy="selectin")

    @property
    def file_link(self) -> str:
        """Public helper cho frontend — trả về GCS HTTPS URL."""
        return f"https://storage.googleapis.com/{self.gcs_path}"


class DocumentReview(Base):
    __tablename__ = "document_reviews"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    grade:       Mapped[int]       = mapped_column(Integer, nullable=False)   # 1-10
    comment:     Mapped[str]       = mapped_column(Text, nullable=False)
    user_id:     Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["Document"] = relationship(back_populates="reviews")
