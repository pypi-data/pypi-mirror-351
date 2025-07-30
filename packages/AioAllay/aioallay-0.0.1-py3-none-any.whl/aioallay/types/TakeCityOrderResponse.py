from pydantic import BaseModel

class TakeCityOrderResponse(BaseModel):
    ok: bool
    message: str
