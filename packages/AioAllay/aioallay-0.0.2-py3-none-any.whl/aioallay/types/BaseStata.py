from typing import Optional

from pydantic import BaseModel, ConfigDict

from aioallay.types.GameSession import GameSession


class BaseStata(BaseModel):
    kill: int
    dead: int
    mobs: int
    fish: int
    ate: int
    destroy_block: int
    last_session: GameSession or None
    place_block: int