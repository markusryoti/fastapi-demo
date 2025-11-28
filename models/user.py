import datetime
import uuid

from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    password: str
    created_at: datetime.datetime = datetime.datetime.now()
