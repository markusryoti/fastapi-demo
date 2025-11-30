import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from app.domain.user import User
from app.repository.todo import TodoRepository, TodoRepositoryInterface
from app.services.todo import TodoService
from app.infrastructure.db import get_session
from pydantic import BaseModel
from app.routers.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.errors import ForbiddenException, NotFoundException


router = APIRouter()


class TodoDto(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    completed: bool = False
    created_at: datetime = datetime.now()
    user_id: uuid.UUID


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
):
    todos = await service.list_user_todos(user)
    return {"todos": [TodoDto(**todo.__dict__) for todo in todos]}


@router.get("/{id}")
async def read_item(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
):
    try:
        todo = await service.get_todo_by_id(id, user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")

    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto(**todo.__dict__)


class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


@router.post("/")
async def post_todo(
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
):
    try:
        created = await service.create_todo(
            todo.title, todo.description, todo.completed, user
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto(**created.__dict__)


@router.put("/{id}")
async def put_todo(
    id: uuid.UUID,
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
):
    try:
        updated = await service.update_todo(
            id, todo.title, todo.description, todo.completed, user
        )
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto(**updated.__dict__)


@router.delete("/{id}")
async def remove_todo(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: TodoService = Depends(get_todo_service),
):
    try:
        await service.delete_todo(id, user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Todo not found")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"message": "Todo deleted"}
