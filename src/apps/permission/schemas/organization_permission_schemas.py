from pydantic import BaseModel, Field
from typing import List, Optional
from src.enums.base import Action, OrganizationModule


class OrganizationPermissionBaseSchema(BaseModel):
    name: str = Field(..., description="Permission group name, e.g., 'Moderators'")
    description: Optional[str] = Field(None)
    actions: List[Action]
    resources: List[OrganizationModule]


class OrganizationPermissionCreateSchema(OrganizationPermissionBaseSchema):
    pass


class OrganizationPermissionUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    actions: Optional[List[Action]]
    resources: Optional[List[OrganizationModule]]


class OrganizationPermissionObjectSchema(OrganizationPermissionBaseSchema):
    id: str
    organization_id: str

    class Config:
        from_attributes = True
