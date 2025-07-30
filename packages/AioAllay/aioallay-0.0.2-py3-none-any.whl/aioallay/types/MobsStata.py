from pydantic import BaseModel

from aioallay.types.GameProfile import GameProfile


class MobsStata(BaseModel):
    mob_type: str
    mob_name: str
    count: int
    game_profile: GameProfile
