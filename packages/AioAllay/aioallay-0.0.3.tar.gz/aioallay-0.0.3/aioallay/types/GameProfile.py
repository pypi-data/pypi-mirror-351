from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class GameProfile(BaseModel):


    id: int
    xbox: str
    create_at: datetime | None | List[int]
    xuid: int | None
    uuid: str | None