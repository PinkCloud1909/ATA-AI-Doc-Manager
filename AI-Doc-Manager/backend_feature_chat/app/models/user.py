import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name:   Mapped[str]       = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None]= mapped_column(Text)

    privileges:  Mapped[list["Privilege"]] = relationship(back_populates="role", lazy="selectin")
    user_roles:  Mapped[list["UserRole"]]  = relationship(back_populates="role")


class Privilege(Base):
    __tablename__ = "privileges"

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id:      Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    api_endpoint: Mapped[str]       = mapped_column(String(255), nullable=False)
    is_allowed:   Mapped[bool]      = mapped_column(Boolean, default=True)

    role: Mapped["Role"] = relationship(back_populates="privileges")


class User(Base):
    __tablename__ = "users"

    id:                    Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid:          Mapped[str]          = mapped_column(String(128), unique=True, nullable=False, index=True)
    username:              Mapped[str]          = mapped_column(String(100), nullable=False)
    email:                 Mapped[str]          = mapped_column(String(255), unique=True, nullable=False)
    last_password_changed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at:            Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_roles:    Mapped[list["UserRole"]]    = relationship(back_populates="user", lazy="selectin")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user")


class UserRole(Base):
    __tablename__ = "user_roles"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:     Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_id:     Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="user_roles", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship(back_populates="user_roles", lazy="selectin")
