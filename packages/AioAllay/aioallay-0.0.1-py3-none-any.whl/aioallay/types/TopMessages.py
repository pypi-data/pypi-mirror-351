from pydantic import BaseModel
from typing import Dict

class TopMessages(BaseModel):
    messages: Dict[str, int]
