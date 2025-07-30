from pydantic import BaseModel

from aioallay.types.GameProfile import GameProfile


class FishStata(BaseModel):
    item_type: str
    item_name: str
    item_meta: str
    count: int
    game_profile: GameProfile





