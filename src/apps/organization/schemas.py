from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from src.utilities.base_schema import AccountBaseModel

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


class OrganizationCreateSchema(AccountBaseModel):
    name: str = Field(..., max_length=55)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrganizationUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=55)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=18)
    password: Optional[str] = Field(None, max_length=128)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrganizationObjectSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., max_length=55)
    email: EmailStr
    phone_number: str = Field(..., max_length=18)
    password: str = Field(..., max_length=128)
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "populate_by_name": True, 
        "json_encoders": {ObjectId: str}
    }


class OrganizationLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=128)
