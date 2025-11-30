import uuid

from app.domain.todo import Todo
from app.domain.user import User
from app.repository.todo import TodoRepositoryInterface
from app.shared.errors import ForbiddenException, NotFoundException


class TodoService:
    def __init__(self, todo_repository: TodoRepositoryInterface):
        self.todo_repository = todo_repository

    async def list_user_todos(self, user: User) -> list[Todo]:
        return await self.todo_repository.list_user_todos(user.id)

    async def create_todo(
        self, title: str, description: str, completed: bool, user: User
    ) -> Todo:
        todo = Todo(
            id=uuid.uuid4(),
            user_id=user.id,
            title=title,
            description=description,
            completed=completed,
        )

        return await self.todo_repository.create_todo(todo)

    async def get_todo_by_id(self, todo_id: uuid.UUID, user: User) -> Todo:
        todo = await self.todo_repository.get_todo_by_id(todo_id)
        if todo is None:
            raise NotFoundException("Todo not found")

        if todo.user_id != user.id:
            raise ForbiddenException("Forbidden")

        return todo

    async def update_todo(
        self,
        todo_id: uuid.UUID,
        title: str,
        description: str,
        completed: bool,
        user: User,
    ) -> Todo:
        existing_todo = await self.todo_repository.get_todo_by_id(todo_id)
        if not existing_todo:
            raise NotFoundException("Todo not found")

        if existing_todo.user_id != user.id:
            raise ForbiddenException("Forbidden")

        updated_todo = Todo(
            id=existing_todo.id,
            user_id=existing_todo.user_id,
            title=title,
            description=description,
            completed=completed,
            created_at=existing_todo.created_at,
        )

        return await self.todo_repository.update_todo(updated_todo)

    async def delete_todo(self, todo_id: uuid.UUID, user: User) -> None:
        existing_todo = await self.todo_repository.get_todo_by_id(todo_id)
        if not existing_todo:
            raise NotFoundException("Todo not found")

        if existing_todo.user_id != user.id:
            raise ForbiddenException("Forbidden")

        await self.todo_repository.delete_todo(todo_id)
