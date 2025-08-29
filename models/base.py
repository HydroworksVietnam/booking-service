from beanie import Document
from pydantic import Field
from datetime import datetime
from beanie import Document, PydanticObjectId

class BaseDocument(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        abstract = True

Base = BaseDocument