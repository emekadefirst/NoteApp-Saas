from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from src.enums.base import Action, Module, OrganizationModule


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


# ---------- Admin Permission (AP) ----------
class APCSchema(BaseModel):
    module: Module 
    action: Action = Action.READ


class APUSchema(BaseModel):
    module: Optional[Module] = None
    action: Optional[Action] = None


class APObjectSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    module: Module
    action: Action
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }


class APGCSchema(BaseModel):
    name: str = Field(..., max_length=125)
    permissions: List[PyObjectId]


class APGUSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=125)
    permissions: Optional[List[PyObjectId]] = None


class APGObjectSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    permissions: List[PyObjectId]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }



class OPSchema(BaseModel):
    """Schema for organization-level permission"""
    module: OrganizationModule 
    action: Action = Action.READ



class OPGCSchema(BaseModel):
    """Schema for creating organization permission groups"""
    name: str = Field(..., max_length=125)
    permissions: List[PyObjectId]


class OPGUSchema(BaseModel):
    """Schema for updating organization permission groups"""
    name: Optional[str] = Field(None, max_length=125)
    permissions: Optional[List[PyObjectId]] = None


class OPGObjectSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    permissions: List[PyObjectId]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }
