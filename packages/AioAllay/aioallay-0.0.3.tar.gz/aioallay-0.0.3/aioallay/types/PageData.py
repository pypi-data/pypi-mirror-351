from pydantic import BaseModel


class PageData(BaseModel):
    size: int
    number: int
    totalElements: int
    totalPages: int