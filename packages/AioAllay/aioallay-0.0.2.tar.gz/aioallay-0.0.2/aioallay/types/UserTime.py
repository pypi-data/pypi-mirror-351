from pydantic import BaseModel


class UserTime(BaseModel):
    xbox: str
    totalTime: str