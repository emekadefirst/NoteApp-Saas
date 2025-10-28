from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class NoteCreateSchema(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    user_id: Optional[str] = None


class NoteUpdateSchema(BaseModel):
    title: Optional[str] = Field(..., max_length=255)
    content: Optional[str] = None

class NoteObjectSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., max_length=255)
    content: str
    user_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "populate_by_name": True, 
        "json_encoders": {ObjectId: str}
    }
