
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from aioallay.types.User import User


class Donate(BaseModel):

    money: float
    user: User
    create_at: Optional[datetime]