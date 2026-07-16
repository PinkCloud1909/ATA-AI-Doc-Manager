import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.shared.utils import utcnow


class DocumentReview(Base):
    __tablename__ = "document_reviews"
    __table_args__ = (
        CheckConstraint("grade BETWEEN 1 AND 10", name="ck_document_reviews_grade"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    created_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        default=utcnow,
    )

    document: Mapped["Document | None"] = relationship(back_populates="reviews")
    user: Mapped["User | None"] = relationship(back_populates="reviews")
