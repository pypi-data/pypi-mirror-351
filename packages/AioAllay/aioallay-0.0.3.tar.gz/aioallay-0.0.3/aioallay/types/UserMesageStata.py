from pydantic import BaseModel

from aioallay.types.User import User


class UserMessageStata(BaseModel):
    user: User
    count: int 