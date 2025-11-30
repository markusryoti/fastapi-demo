import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo import Todo
from app.infrastructure.models import TodoDao
from app.shared.errors import NotFoundException


class TodoRepositoryInterface(ABC):
    @abstractmethod
    async def create_todo(self, todo: Todo) -> Todo:
        pass

    @abstractmethod
    async def get_todo_by_id(self, todo_id: uuid.UUID) -> Todo | None:
        pass

    @abstractmethod
    async def update_todo(self, todo: Todo) -> Todo:
        pass

    @abstractmethod
    async def delete_todo(self, todo_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def list_user_todos(self, user_id: uuid.UUID) -> list:
        pass


class TodoRepository(TodoRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_todo(self, todo: Todo) -> Todo:
        todo_dao = TodoDao(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            user_id=todo.user_id,
            completed=todo.completed,
            created_at=todo.created_at,
        )
        self.session.add(todo_dao)
        await self.session.flush()
        await self.session.refresh(todo_dao)
        return TodoRepository.dao_to_domain(todo_dao)

    async def get_todo_by_id(self, todo_id: uuid.UUID) -> Todo | None:
        query = select(TodoDao).where(TodoDao.id == todo_id).limit(1)
        result = await self.session.execute(query)
        todo = result.scalars().first()
        return TodoRepository.dao_to_domain(todo) if todo else None

    async def update_todo(self, todo: Todo) -> Todo:
        result = await self.session.execute(
            select(TodoDao).where(TodoDao.id == todo.id).with_for_update()
        )

        existing = result.scalar_one_or_none()

        if not existing:
            raise NotFoundException("Todo not found")

        existing.title = todo.title
        existing.description = todo.description
        existing.completed = todo.completed

        await self.session.flush()

        return TodoRepository.dao_to_domain(existing)

    async def delete_todo(self, todo_id: uuid.UUID) -> None:
        query = select(TodoDao).where(TodoDao.id == todo_id).limit(1)
        result = await self.session.execute(query)
        todo = result.scalars().first()

        if not todo:
            raise NotFoundException("Todo not found")

        await self.session.delete(todo)
        await self.session.flush()

    async def list_user_todos(self, user_id: uuid.UUID) -> list[Todo]:
        query = select(TodoDao).where(TodoDao.user_id == user_id)
        result = await self.session.execute(query)
        todos = result.scalars().all()
        return [TodoRepository.dao_to_domain(t) for t in todos]

    @staticmethod
    def dao_to_domain(todo_dao: TodoDao) -> Todo:
        return Todo(
            id=todo_dao.id,
            title=todo_dao.title,
            description=todo_dao.description,
            user_id=todo_dao.user_id,
            completed=todo_dao.completed,
            created_at=todo_dao.created_at,
        )
