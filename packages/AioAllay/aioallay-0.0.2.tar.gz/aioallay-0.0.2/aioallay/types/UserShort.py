from pydantic import BaseModel


class UserShort(BaseModel):
    id: int
    xbox: str
    name: str