from datetime import datetime

from pydantic import BaseModel

from aioallay.types.User import User


class SimpleMarket(BaseModel):
    id: int
    content: str
    user: User
    create_at: datetime