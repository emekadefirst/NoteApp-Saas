from datetime import datetime
from typing import List, Optional, Union
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from src.enums.base import Action, Module


# -------------------------------------------------------------------
# ✅ Pydantic v2 compatible ObjectId field
# -------------------------------------------------------------------
class PyObjectId(ObjectId):
    """Custom ObjectId type compatible with Pydantic v2."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        """Ensures this shows as string in OpenAPI docs"""
        json_schema: JsonSchemaValue = handler(schema)
        json_schema.update(type="string", examples=["6561f2c7cde75e9a3fd8b57b"])
        return json_schema

    @classmethod
    def validate(cls, v):
        """Validate and cast input to ObjectId"""
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def serialize(cls, v):
        return str(v)


# -------------------------------------------------------------------
# ✅ Permission Schema
# -------------------------------------------------------------------
class PermissionObjectSchema(BaseModel):
    """Represents a single permission action-resource pair."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    action: Action
    resource: Module
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        },
    }


# -------------------------------------------------------------------
# ✅ Permission Group Schema
# -------------------------------------------------------------------
class PermissionGroupObjectSchema(BaseModel):
    """Group of permissions assigned to roles or entities."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    permissions: List[Union[PyObjectId, PermissionObjectSchema]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        },
    }


# -------------------------------------------------------------------
# ✅ Creation Schemas
# -------------------------------------------------------------------
class PermissionCreateSchema(BaseModel):
    """Schema for creating a new permission."""
    action: Action
    resource: Module


class PermissionGroupCreateSchema(BaseModel):
    """Schema for creating a new permission group."""
    name: str
    permissions: List[PyObjectId] = []


# -------------------------------------------------------------------
# ✅ Update Schemas
# -------------------------------------------------------------------
class PermissionUpdateSchema(BaseModel):
    """Schema for updating a permission."""
    action: Optional[Action] = None
    resource: Optional[Module] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PermissionGroupUpdateSchema(BaseModel):
    """Schema for updating a permission group."""
    name: Optional[str] = None
    permissions: Optional[List[PyObjectId]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
