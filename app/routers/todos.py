from datetime import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import TodoDao
from .users import User

from infrastructure.db.db import get_db
from routers.auth import get_current_user

router = APIRouter()


class Todo(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    completed: bool = False
    created_at: datetime = datetime.now()
    user_id: uuid.UUID


@router.get("/")
async def read_todos(
    user: Annotated[User, Depends(get_current_user)], db: AsyncSession = Depends(get_db)
):
    query = select(TodoDao).where(TodoDao.user_id == user.id)
    result = await db.execute(query)
    todos = result.scalars().all()
    return [Todo(**t.__dict__) for t in todos]


@router.get("/{id}")
async def read_item(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    query = select(TodoDao).where(TodoDao.id == id).limit(1)
    result = await db.execute(query)
    todo = result.scalars().first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return Todo(**todo.__dict__) if todo else None


class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


@router.post("/")
async def post_todo(
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    new_todo = TodoDao(
        user_id=user.id,
        title=todo.title,
        description=todo.description,
    )

    db.add(new_todo)

    await db.commit()
    await db.refresh(new_todo)

    return Todo(**new_todo.__dict__)


@router.put("/{id}")
async def put_todo(
    id: uuid.UUID,
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
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

    return Todo(**existing.__dict__)


@router.delete("/{id}")
async def remove_todo(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
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
