from datetime import datetime
import uuid
from fastapi import APIRouter
from pydantic import BaseModel

from services.users import fake_users_db

router = APIRouter()


class User(BaseModel):
    id: uuid.UUID
    email: str
    password: str
    created_at: datetime = datetime.now()


@router.get("/")
async def read_users():
    users = list(map(lambda user: User(**user), fake_users_db.values()))
    return {"users": users}
