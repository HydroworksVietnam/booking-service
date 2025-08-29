from pydantic import Field
from .base import BaseDocument
from typing import List
from pydantic import Field


class Service(BaseDocument):
    name: str
    description: str
    duration: int
    price: float
    photos: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)

    class Settings:
        name = "services"