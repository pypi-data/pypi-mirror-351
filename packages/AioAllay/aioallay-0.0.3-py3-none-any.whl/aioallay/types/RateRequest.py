from pydantic import BaseModel


class RateRequest(BaseModel):
    user_id: int
    admin_id: int
    count: int
    text: str