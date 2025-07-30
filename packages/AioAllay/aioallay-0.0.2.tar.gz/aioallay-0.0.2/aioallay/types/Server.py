from pydantic import BaseModel


class Server(BaseModel):
    name: str
    ip: str
    port: int
    whitelist_mode: int
    photo_url: str | None
    news_title: str | None
    news: str | None