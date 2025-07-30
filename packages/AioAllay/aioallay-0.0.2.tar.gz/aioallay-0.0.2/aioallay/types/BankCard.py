import datetime

from pydantic import BaseModel


class BankCard(BaseModel):
    id: int
    image_id: int
    money: int
    number: int
    create_at: datetime.datetime
    name: str
    is_locked: bool

