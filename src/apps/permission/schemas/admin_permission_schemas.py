from pydantic import BaseModel, Field
from typing import List, Optional
from src.enums.base import Action, OrganizationModule


class AdminPermissionBaseSchema(BaseModel):
    """
    Base schema for defining admin-level permissions.
    """
    name: str = Field(..., description="Permission name, e.g., 'Manage Users'")
    description: Optional[str] = Field(None, description="What this permission allows")
    actions: List[Action] = Field(..., description="List of allowed actions")
    resources: List[OrganizationModule] = Field(..., description="Modules this applies to")


class AdminPermissionCreateSchema(AdminPermissionBaseSchema):
    pass


class AdminPermissionUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    actions: Optional[List[Action]]
    resources: Optional[List[OrganizationModule]]


class AdminPermissionObjectSchema(AdminPermissionBaseSchema):
    id: str

    class Config:
        from_attributes = True
