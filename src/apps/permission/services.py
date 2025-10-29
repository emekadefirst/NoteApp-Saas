from src.apps.permission.schemas import (
    PermissionObjectSchema,
    PermissionGroupObjectSchema,
)
from src.errors.base import ErrorHandler
from src.core.database import get_collection
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId


class PermissionService:
    error = ErrorHandler("Permission")

    @classmethod
    async def get_collection(cls):
        return await get_collection("Permissions")

    @classmethod
    async def create(cls, dto: PermissionObjectSchema):
        """Create a new permission"""
        collection = await cls.get_collection()
        dto.created_at = datetime.utcnow()
        result = await collection.insert_one(dto.model_dump(by_alias=True))
        return str(result.inserted_id)

    @classmethod
    async def get_all(cls):
        """Fetch all permissions"""
        collection = await cls.get_collection()
        return await collection.find({}).to_list(length=None)

    @classmethod
    async def get_by_id(cls, permission_id: str):
        """Fetch a single permission by ID"""
        try:
            obj_id = ObjectId(permission_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid permission ID")

        collection = await cls.get_collection()
        permission = await collection.find_one({"_id": obj_id})
        if not permission:
            raise cls.error.get(404, "Permission not found")
        return permission

    @classmethod
    async def update(cls, permission_id: str, dto: PermissionObjectSchema):
        """Update a permission"""
        try:
            obj_id = ObjectId(permission_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid permission ID")

        collection = await cls.get_collection()
        dto.updated_at = datetime.utcnow()
        update_data = {k: v for k, v in dto.model_dump(by_alias=True).items() if v is not None}

        result = await collection.update_one({"_id": obj_id}, {"$set": update_data})
        if result.modified_count == 0:
            raise cls.error.get(404, "Permission not found or not modified")

        return {"message": "Permission updated successfully"}

    @classmethod
    async def delete(cls, permission_id: str):
        """Delete a permission"""
        try:
            obj_id = ObjectId(permission_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid permission ID")

        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            raise cls.error.get(404, "Permission not found")

        return {"message": "Permission deleted successfully"}


class PermissionGroupService:
    error = ErrorHandler("PermissionGroup")

    @classmethod
    async def get_collection(cls):
        return await get_collection("PermissionGroups")

    @classmethod
    async def create(cls, dto: PermissionGroupObjectSchema):
        """Create a new permission group"""
        collection = await cls.get_collection()
        dto.created_at = datetime.utcnow()
        result = await collection.insert_one(dto.model_dump(by_alias=True))
        return str(result.inserted_id)

    @classmethod
    async def add_permission(cls, group_id: str, permission_id: str):
        """Add a permission to a group"""
        try:
            group_obj_id = ObjectId(group_id)
            perm_obj_id = ObjectId(permission_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid ID format")

        collection = await cls.get_collection()
        result = await collection.update_one(
            {"_id": group_obj_id},
            {"$addToSet": {"permissions": perm_obj_id}, "$set": {"updated_at": datetime.utcnow()}},
        )
        if result.modified_count == 0:
            raise cls.error.get(404, "Permission group not found or already contains this permission")
        return {"message": "Permission added to group"}

    @classmethod
    async def get_all(cls):
        """Fetch all permission groups"""
        collection = await cls.get_collection()
        return await collection.find({}).to_list(length=None)

    @classmethod
    async def get_by_id(cls, group_id: str):
        """Fetch one group and expand permissions"""
        try:
            obj_id = ObjectId(group_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid group ID")

        collection = await cls.get_collection()
        group = await collection.find_one({"_id": obj_id})
        if not group:
            raise cls.error.get(404, "Permission group not found")

        # Expand permission details
        perm_collection = await get_collection("Permissions")
        group["permissions"] = await perm_collection.find(
            {"_id": {"$in": group.get("permissions", [])}}
        ).to_list(length=None)

        return group

    @classmethod
    async def update(cls, group_id: str, dto: PermissionGroupObjectSchema):
        """Update permission group"""
        try:
            obj_id = ObjectId(group_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid group ID")

        collection = await cls.get_collection()
        dto.updated_at = datetime.utcnow()
        update_data = {k: v for k, v in dto.model_dump(by_alias=True).items() if v is not None}

        result = await collection.update_one({"_id": obj_id}, {"$set": update_data})
        if result.modified_count == 0:
            raise cls.error.get(404, "Permission group not found or not modified")

        return {"message": "Permission group updated successfully"}

    @classmethod
    async def delete(cls, group_id: str):
        """Delete a permission group"""
        try:
            obj_id = ObjectId(group_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid group ID")

        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            raise cls.error.get(404, "Permission group not found")

        return {"message": "Permission group deleted successfully"}
