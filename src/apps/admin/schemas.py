from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict, Union
from datetime import datetime
from bson import ObjectId
from src.enums.base import AdminRole
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


class AdminUserCreateSchema(AccountBaseModel):
    first_name: str = Field(..., max_length=55)
    last_name: str = Field(..., max_length=55)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None   


class AdminUserUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, max_length=55)
    last_name: Optional[str] = Field(None, max_length=55)
    email: Optional[EmailStr] = None
    role: Optional[AdminRole] = None
    phone_number: Optional[str] = Field(None, max_length=18)
    password: Optional[str] = Field(None, max_length=128)


class AdminLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=128)


class AdminObjectSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str = Field(..., max_length=55)
    last_name: str = Field(..., max_length=55)
    email: EmailStr
    role: AdminRole
    permission_groups: List[PyObjectId] | None = []
    phone_number: str = Field(..., max_length=18)
    password: str = Field(..., max_length=128)
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }

    @field_validator("permission_groups", mode="before")
    def ensure_list(cls, v):
        """Convert single ObjectId → list[ObjectId]."""
        if v is None:
            return []
        if isinstance(v, ObjectId):
            return [v]
        return v
