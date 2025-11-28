import datetime
import uuid

from pydantic import BaseModel


class Todo(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    completed: bool = False
    created_at: datetime.datetime = datetime.datetime.now()
    user_id: uuid.UUID
