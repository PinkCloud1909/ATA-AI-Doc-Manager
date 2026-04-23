import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    privileges: Mapped[list["Privilege"]] = relationship(back_populates="role")
    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="role")


class Privilege(Base):
    __tablename__ = "privileges"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("roles.id"),
        nullable=True,
        index=True,
    )
    api_endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    is_allowed: Mapped[bool | None] = mapped_column(nullable=True)

    role: Mapped["Role | None"] = relationship(back_populates="privileges")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_password_changed: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        foreign_keys="UserRole.user_id",
    )
    assigned_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="assigned_by_user",
        foreign_keys="UserRole.assigned_by",
    )
    created_documents: Mapped[list["Document"]] = relationship(
        back_populates="creator",
        foreign_keys="Document.created_by",
    )
    modified_documents: Mapped[list["Document"]] = relationship(
        back_populates="modifier",
        foreign_keys="Document.modified_by",
    )
    reviews: Mapped[list["DocumentReview"]] = relationship(back_populates="user")


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="user_roles",
        foreign_keys=[user_id],
    )
    role: Mapped["Role"] = relationship(back_populates="user_roles")
    assigned_by_user: Mapped["User | None"] = relationship(
        back_populates="assigned_roles",
        foreign_keys=[assigned_by],
    )
