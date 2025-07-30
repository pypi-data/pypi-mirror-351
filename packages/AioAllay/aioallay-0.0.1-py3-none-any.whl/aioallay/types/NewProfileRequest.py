from typing import Optional

from pydantic import BaseModel


class NewProfileData:
    telegram_id: Optional[int] | None
    xbox: Optional[str] | None
    name: Optional[str] | None
    age: Optional[str] | None
    sex: Optional[str] | None
    country: Optional[str] | None



class NewProfileRequest(BaseModel):
    telegramId: Optional[int] | None
    xbox: Optional[str] | None
    name: Optional[str] | None
    age: Optional[str] | None
    sex: Optional[str] | None
    country: Optional[str] | None

class MarketItem(BaseModel):
    content: Optional[str] | None
    userId: Optional[int] | None

