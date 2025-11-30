import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo import Todo
from app.domain.user import User
from app.infrastructure.db import get_session
from app.repository.todo import TodoRepository, TodoRepositoryInterface
from app.routers.auth import get_current_user
from app.services.todo import TodoService
from app.shared.errors import ForbiddenException, NotFoundException

router = APIRouter()


class TodoDto(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    completed: bool = False
    created_at: datetime = datetime.now()
    user_id: uuid.UUID

    @staticmethod
    def from_domain(todo: Todo):
        return TodoDto(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            created_at=todo.created_at,
            user_id=todo.user_id,
        )


def get_todo_repository(session: AsyncSession = Depends(get_session)) -> TodoRepository:
    return TodoRepository(session)


def get_todo_service(
    todo_repository: TodoRepositoryInterface = Depends(get_todo_repository),
) -> TodoService:
    return TodoService(todo_repository)


@router.get("/")
async def read_todos(
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
) -> list[TodoDto]:
    todos = await service.list_user_todos(user)
    return [TodoDto.from_domain(todo) for todo in todos]


@router.get("/{id}")
async def read_item(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
) -> TodoDto:
    try:
        todo = await service.get_todo_by_id(id, user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")

    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto.from_domain(todo)


class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


@router.post("/")
async def post_todo(
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
) -> TodoDto:
    try:
        created = await service.create_todo(
            todo.title, todo.description, todo.completed, user
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto.from_domain(created)


@router.put("/{id}")
async def put_todo(
    id: uuid.UUID,
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
) -> TodoDto:
    try:
        updated = await service.update_todo(
            id, todo.title, todo.description, todo.completed, user
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto.from_domain(updated)


class DeleteResponse(BaseModel):
    message: str


@router.delete("/{id}")
async def remove_todo(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
) -> DeleteResponse:
    try:
        await service.delete_todo(id, user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return DeleteResponse(message="Todo deleted successfully")
