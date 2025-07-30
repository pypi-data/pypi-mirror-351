from pydantic import BaseModel

from aioallay.types.UserShort import UserShort


class CityOrder(BaseModel):
    id: int
    name: str
    resource: str
    price: int
    user: UserShort