from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
)

DATABASE_URL = "sqlite+aiosqlite:///./todos.db"


engine = create_async_engine(DATABASE_URL, echo=True)


async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session():
    async with async_session() as session:
        async with session.begin():
            yield session


class Base(DeclarativeBase):
    pass
