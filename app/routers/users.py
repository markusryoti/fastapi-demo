from datetime import datetime
import uuid
from fastapi import APIRouter
from pydantic import BaseModel

from app.domain.user import User
from app.services.users import fake_users_db

router = APIRouter()


class UserDto(BaseModel):
    id: uuid.UUID
    email: str
    password: str
    created_at: datetime = datetime.now()

    def to_domain(self):
        return User(
            id=self.id,
            email=self.email,
            created_at=self.created_at,
        )


@router.get("/")
async def read_users():
    users = list(map(lambda user: UserDto(**user), fake_users_db.values()))
    return {"users": users}
