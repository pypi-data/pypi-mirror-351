from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from aioallay.types.BankCard import BankCard
from aioallay.types.CityOrder import CityOrder
from aioallay.types.GameProfile import GameProfile


class User(BaseModel):
    id: int
    rate: float
    telegram_id: int
    name: str
    username: str
    bio: Optional[str]
    age: int
    sex: str
    city_weather: Optional[str]
    country: str

    is_deleted: bool
    is_premium: bool
    is_bot: bool
    create_at: datetime
    birthday_at: Optional[datetime]
    game_profiles: List[GameProfile]
    bank_cards: List[BankCard]
    city_orders: List[CityOrder]

    def get_gp(self, xbox: str) -> GameProfile:
        for game_profile in self.game_profiles:
            if game_profile.xbox == xbox:
                return game_profile

#todo
  #  async def update_rate(self, rate: int):
       # new_user: User = await httpClient.update_user_rate(self.id, rate)
        #self.rate = new_user.rate


