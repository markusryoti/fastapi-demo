from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Todo:
    id: uuid.UUID
    title: str
    description: str
    user_id: uuid.UUID
    completed: bool = False
    created_at: datetime = datetime.now()
