from pydantic import BaseModel

from aioallay.types.GameProfile import GameProfile


class BlockStata(BaseModel):
    count: int
    event: str
    block_name: str
    block_type: str
    game_profile: GameProfile
