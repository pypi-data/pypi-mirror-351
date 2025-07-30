from datetime import datetime

from pydantic import BaseModel

from aioallay.types.User import User


class Rate(BaseModel):
    count: float
    user: User
    create_at: datetime
    text: str