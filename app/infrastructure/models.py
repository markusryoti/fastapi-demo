import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .db import Base


class UserDao(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, index=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda x: datetime.now(UTC)
    )

    todos: Mapped[list["TodoDao"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class TodoDao(Base):
    __tablename__ = "todos"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, index=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda x: datetime.now(UTC)
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    user: Mapped["UserDao"] = relationship(back_populates="todos")
