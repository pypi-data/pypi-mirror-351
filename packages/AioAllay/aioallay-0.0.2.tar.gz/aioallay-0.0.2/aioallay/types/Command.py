from datetime import datetime
from typing import List
from pydantic import BaseModel

class Command(BaseModel):
    command: str
    description: str
    cmd_type: str
    roles: List[str]
    create_at: datetime