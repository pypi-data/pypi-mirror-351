from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AllayVersion(BaseModel):
    version: str
    changelog: str
    file: str
    platform: str
    createAt: Optional[datetime]