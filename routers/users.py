from fastapi import APIRouter

from models.user import User
from services.users import fake_users_db

router = APIRouter()


@router.get("/")
async def read_users():
    users = list(map(lambda user: User(**user), fake_users_db.values()))
    return {"users": users}
