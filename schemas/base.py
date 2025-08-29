from pydantic import BaseModel
from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    id: PydanticObjectId | None = Field(None, alias="_id")
    class Config:
        from_attributes = True
        validate_by_name = True


class DateTimeModelMixin(BaseModel):
    created_at: datetime