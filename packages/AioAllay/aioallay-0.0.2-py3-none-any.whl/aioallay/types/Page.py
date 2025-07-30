from typing import TypeVar, Generic, List

from pydantic import BaseModel

from aioallay.types.PageData import PageData

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    content: List[T]
    page: PageData