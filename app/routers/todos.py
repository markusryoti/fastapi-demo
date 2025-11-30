import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from app.domain.user import User
from app.repository.todo import TodoRepository
from app.services.todo import TodoService
from app.infrastructure.db import get_session
from app.infrastructure.models import TodoDao
from pydantic import BaseModel
from app.routers.auth import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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
    todo_repository: TodoRepository = Depends(get_todo_repository),
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
    db: AsyncSession = Depends(get_session),
):
    query = select(TodoDao).where(TodoDao.id == id).limit(1)
    result = await db.execute(query)
    todo = result.scalars().first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TodoDto(**todo.__dict__) if todo else None


class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


@router.post("/")
async def post_todo(
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    new_todo = TodoDao(
        user_id=user.id,
        title=todo.title,
        description=todo.description,
    )

    db.add(new_todo)

    await db.commit()
    await db.refresh(new_todo)

    return TodoDto(**new_todo.__dict__)


@router.put("/{id}")
async def put_todo(
    id: uuid.UUID,
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    query = select(TodoDao).where(TodoDao.id == id).limit(1)
    result = await db.execute(query)
    existing = result.scalars().first()

    if not existing:
        raise HTTPException(status_code=404, detail="Todo not found")

    if existing.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    existing.title = todo.title
    existing.description = todo.description
    existing.completed = todo.completed

    await db.commit()
    await db.refresh(existing)

    return TodoDto(**existing.__dict__)


@router.delete("/{id}")
async def remove_todo(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    query = select(TodoDao).where(TodoDao.id == id).limit(1)
    result = await db.execute(query)
    todo = result.scalars().first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.delete(todo)
    await db.commit()

    return {"message": "Todo deleted"}
