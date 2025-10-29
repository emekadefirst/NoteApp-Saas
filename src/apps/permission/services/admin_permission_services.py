from src.core.database import get_collection
from src.errors.base import ErrorHandler
from src.apps.permission.schemas.admin_permission_schemas import (
    AdminPermissionCreateSchema, AdminPermissionUpdateSchema
)
from bson import ObjectId


class AdminPermissionService:
    error = ErrorHandler("AdminPermission")

    @classmethod
    async def get_collection(cls):
        return await get_collection("AdminPermissions")

    @classmethod
    async def create(cls, dto: AdminPermissionCreateSchema):
        collection = await cls.get_collection()
        data = dto.model_dump()
        result = await collection.insert_one(data)
        return {**data, "id": str(result.inserted_id)}

    @classmethod
    async def get_all(cls):
        collection = await cls.get_collection()
        permissions = await collection.find({}).to_list(length=None)
        for p in permissions:
            p["id"] = str(p["_id"])
        return permissions

    @classmethod
    async def update(cls, id: str, dto: AdminPermissionUpdateSchema):
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
