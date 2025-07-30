from pydantic import BaseModel
from aioallay.types.User import User


class RateTop(BaseModel):
    count: float
    user: User