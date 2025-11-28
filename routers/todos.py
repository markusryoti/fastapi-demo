import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from infrastructure.db.db import TodoDao, get_db
from models.todo import Todo
from models.user import User
from routers.auth import get_current_user

router = APIRouter()


@router.get("/")
def read_todos(
    user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)
):
    todos = db.query(TodoDao).filter(TodoDao.user_id == user.id).all()
    return [Todo(**t.__dict__) for t in todos]


@router.get("/{id}")
def read_item(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    todo = db.query(TodoDao).filter(TodoDao.id == id).first()

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
def post_todo(
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    new_todo = TodoDao(
        user_id=user.id,
        title=todo.title,
        description=todo.description,
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return Todo(**new_todo.__dict__)


@router.put("/{id}")
def put_todo(
    id: uuid.UUID,
    todo: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    existing = db.query(TodoDao).filter(TodoDao.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Todo not found")

    if existing.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    existing.title = todo.title
    existing.description = todo.description
    existing.completed = todo.completed

    db.commit()
    db.refresh(existing)

    return Todo(**existing.__dict__)


@router.delete("/{id}")
def remove_todo(
    id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    todo = db.query(TodoDao).filter(TodoDao.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted"}
