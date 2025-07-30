from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, List

from data.GameProfile import GameProfile


@dataclass
class PlayerContainerChangeDTO:
    event: str
    xbox: str
    xuid: int
    x: int
    y: int
    z: int
    dim: int
    old_type: str
    old_name: str
    old_item_count: int
    new_type: str
    new_name: str
    new_item_count: int
    slot: int
    block_type: str
    block_name: str

class BlockEventLog(BaseModel):
    create_at: List[int]
    id: Optional[int] = None
    xuid: int
    name: str
    event: str
    x: int
    y: int
    z: int
    dim: int
    type: str
    game_profile: GameProfile

class LogsSecurityDTO(BaseModel):
    event: str
    item: Optional[PlayerContainerChangeDTO] = None
    block: Optional[BlockEventLog] = None
