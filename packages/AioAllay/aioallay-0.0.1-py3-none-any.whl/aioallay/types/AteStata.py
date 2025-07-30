from pydantic import BaseModel

from aioallay.types.GameProfile import GameProfile

class AteStata(BaseModel):
    item_type: str
    item_name: str
    count: int
    game_profile: GameProfile

