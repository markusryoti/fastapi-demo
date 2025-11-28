import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


class Base(DeclarativeBase):
    pass


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


if __name__ == "__main__":
    engine = create_engine("sqlite://", echo=True)
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    with Session() as session:
        user = UserDao(email="test@example.com", password="password")
        session.add(user)

        todo = TodoDao(title="Test Todo", description="Test Description", user=user)
        session.add(todo)

        session.commit()
