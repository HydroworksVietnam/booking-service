from pydantic import Field
from .base import BaseSchema
from beanie import PydanticObjectId
from typing import Optional, List


class ServiceBase(BaseSchema):
    name: str
    description: str | None = None
    duration: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    photos: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    name: str | None = None
    duration: int | None = Field(None, gt=0)
    price: float | None = Field(None, gt=0)

class ServiceOut(ServiceBase):
    id: PydanticObjectId
    
    class Config:
        json_encoders = {
            PydanticObjectId: str
        }