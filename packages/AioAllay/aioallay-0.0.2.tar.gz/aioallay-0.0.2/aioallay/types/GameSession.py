from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameSession(BaseModel):


    id: int
    xuid: int
    xbox: str
    startAt: datetime
    endAt: datetime
    totalTime: str