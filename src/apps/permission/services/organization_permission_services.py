from src.core.database import get_collection
from src.errors.base import ErrorHandler
from src.apps.permission.schemas.organization_permission_schemas import (
    OrganizationPermissionCreateSchema, OrganizationPermissionUpdateSchema
)
from bson import ObjectId


class OrganizationPermissionService:
    error = ErrorHandler("OrganizationPermission")

    @classmethod
    async def get_collection(cls):
        return await get_collection("OrganizationPermissions")

    @classmethod
    async def create(cls, dto: OrganizationPermissionCreateSchema, organization_id: str):
        collection = await cls.get_collection()
        data = dto.model_dump()
        data["organization_id"] = ObjectId(organization_id)
        result = await collection.insert_one(data)
        return {**data, "id": str(result.inserted_id)}

    @classmethod
    async def get_all(cls, organization_id: str):
        collection = await cls.get_collection()
        permissions = await collection.find(
            {"organization_id": ObjectId(organization_id)}
        ).to_list(length=None)
        for p in permissions:
            p["id"] = str(p["_id"])
        return permissions

    @classmethod
    async def update(cls, id: str, dto: OrganizationPermissionUpdateSchema):
        collection = await cls.get_collection()
        update_data = {k: v for k, v in dto.model_dump().items() if v is not None}
        result = await collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.modified_count == 0:
            raise cls.error.not_found("Permission not found")
        return {"message": "Permission updated successfully"}

    @classmethod
    async def delete(cls, id: str):
        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise cls.error.not_found("Permission not found")
        return {"message": "Permission deleted successfully"}
