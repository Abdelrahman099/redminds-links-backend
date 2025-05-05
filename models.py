from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        
    def __repr__(self):
        return f"PyObjectId({super().__repr__()})"

class LinkSchema(BaseModel):
    url: HttpUrl = Field(...)
    name: str = Field(..., min_length=1)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True, # required for the ObjectId
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "url": "https://example.com",
                "name": "Example Site"
            }
        },
        "from_attributes": True
    }

class LinkDB(LinkSchema):
    id: str = Field(default=None, alias="_id")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "from_attributes": True
    }

class UpdateLinkModel(BaseModel):
    url: Optional[HttpUrl] = None
    name: Optional[str] = None

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "url": "https://newexample.com",
                "name": "New Example Site Name"
            }
        },
        "from_attributes": True
    }

