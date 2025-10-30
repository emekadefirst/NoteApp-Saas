from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from src.core.database import get_collection
from src.errors.base import ErrorHandler
from src.apps.permission.schemas import PermissionObjectSchema, PermissionGroupObjectSchema
from src.utilities.serializers import serialize_mongo_doc


class PermissionService:
    error = ErrorHandler("Permission")

    @classmethod
    async def get_collection(cls):
        return await get_collection("Permissions")

    # ✅ Create Permission
    @classmethod
    async def create(cls, data: dict):
        collection = await cls.get_collection()
        data["created_at"] = datetime.utcnow()
        result = await collection.insert_one(data)
        created = await collection.find_one({"_id": result.inserted_id})
        created["_id"] = str(created["_id"])  # 🔧 convert ObjectId to string
        return PermissionObjectSchema(**created)

    # ✅ Get All Permissions
    @classmethod
    async def get_all(cls):
        collection = await cls.get_collection()
        permissions = await collection.find({}).to_list(length=None)
        return serialize_mongo_doc(permissions)

    @classmethod
    async def get_by_id(cls, id: str):
        collection = await cls.get_collection()
        obj = await collection.find_one({"_id": ObjectId(id)})
        if not obj:
            raise cls.error.get(404, "Permission not found")
        return serialize_mongo_doc(obj)

    # ✅ Delete Permission
    @classmethod
    async def delete(cls, permission_id: str):
        try:
            obj_id = ObjectId(permission_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid permission ID")

        collection = await cls.get_collection()
        deleted = await collection.delete_one({"_id": obj_id})
        if not deleted.deleted_count:
            raise cls.error.get(404, "Permission not found")

        return {"message": "Permission deleted successfully"}


class PermissionGroupService:
    error = ErrorHandler("Permission Group")

    @classmethod
    async def get_collection(cls):
        return await get_collection("PermissionGroups")

    # ✅ Create Group
    @classmethod
    async def create(cls, data: dict):
        collection = await cls.get_collection()
        data["created_at"] = datetime.utcnow()
        result = await collection.insert_one(data)
        created = await collection.find_one({"_id": result.inserted_id})
        created["_id"] = str(created["_id"])  # 🔧 fix ObjectId
        return PermissionGroupObjectSchema(**created)

    @classmethod
    async def get_all(cls):
        group_collection = await cls.get_collection()
        groups = await group_collection.find({}).to_list(length=None)
        perm_collection = await get_collection("Permissions")

        for g in groups:
            # Ensure group id is a string
            g["_id"] = str(g["_id"])

            perm_ids = g.get("permissions", [])
            resolved_permissions = []
            if perm_ids:
                # Convert to ObjectIds safely
                perm_obj_ids = [
                    ObjectId(p) if not isinstance(p, ObjectId) else p
                    for p in perm_ids
                    if ObjectId.is_valid(str(p))
                ]

                perms = await perm_collection.find({"_id": {"$in": perm_obj_ids}}).to_list(length=None)
                for p in perms:
                    # Normalize permission object
                    p["_id"] = str(p["_id"])
                    resolved_permissions.append(
                        PermissionObjectSchema(**p).model_dump(by_alias=True)
                    )

            g["permissions"] = resolved_permissions
        return serialize_mongo_doc(groups)

    @classmethod
    async def get_by_id(cls, group_id: str):
        if not ObjectId.is_valid(group_id):
            raise cls.error.get(400, "Invalid group ID")

        group_collection = await cls.get_collection()
        group = await group_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise cls.error.get(404, "Permission group not found")

        perm_collection = await get_collection("Permissions")
        perm_ids = group.get("permissions", [])
        resolved_permissions = []
        if perm_ids:
            perm_obj_ids = [
                ObjectId(p) if not isinstance(p, ObjectId) else p
                for p in perm_ids
                if ObjectId.is_valid(str(p))
            ]
            perms = await perm_collection.find({"_id": {"$in": perm_obj_ids}}).to_list(length=None)
            for p in perms:
                p["_id"] = str(p["_id"])
                resolved_permissions.append(
                    PermissionObjectSchema(**p).model_dump(by_alias=True)
                )

        group["_id"] = str(group["_id"])
        group["permissions"] = resolved_permissions

        return serialize_mongo_doc(group)


    @classmethod
    async def delete(cls, group_id: str):
        try:
            obj_id = ObjectId(group_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid group ID")

        collection = await cls.get_collection()
        deleted = await collection.delete_one({"_id": obj_id})
        if not deleted.deleted_count:
            raise cls.error.get(404, "Permission group not found")

        return {"message": "Permission group deleted successfully"}
