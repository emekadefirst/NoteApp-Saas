from fastapi import Request, HTTPException
from src.errors.base import ErrorHandler
from src.enums.base import Action, Module
from src.core.database import get_collection
from bson import ObjectId
from src.utilities.crypto.jwt import JWTService


class PermissionControl:
    @classmethod
    async def validate_permission(cls, request: Request, action: Action, resource: Module):
        """
        Validate the logged-in user's permission based on user_type.
        """
        user_type = getattr(request.state, "user_type", None)
        user_id = getattr(request.state, "user_id", None)

        if not user_id or not user_type:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if user_type == "admin":
            return await AdminPermissionDependency.has_permission(user_id, action, resource)
        elif user_type == "organization":
            return await OrganizationPermissionDependency.has_permission(user_id, action, resource)
        elif user_type == "user":
            return await UserPermissionDependency.has_permission(user_id, action, resource)
        else:
            raise HTTPException(status_code=403, detail="Invalid user type")


class AdminPermissionDependency:
    error = ErrorHandler("AdminPermission")

    @classmethod
    async def has_permission(cls, user_id: str, action: Action, resource: Module):
        collection = await get_collection("Admins") 
        admin = await collection.find_one({"_id": ObjectId(user_id)})
        if not admin:
            raise cls.error.get(401, "Admin not found")
        if admin.get("role") == "ADMIN":
            return True 
        
        permission_groups = admin.get("permission_groups", [])
        if action in permission_groups:
            return True
        raise cls.error.get(403, f"No permission for {action} on {resource}")

class OrganizationPermissionDependency:
    error = ErrorHandler("OrganizationPermission")
    jwt = JWTService()

    @classmethod
    async def has_permission(cls, user_id: str, action: Action, resource: Module):
        # implement organization permission logic
        ...


class UserPermissionDependency:
    error = ErrorHandler("UserPermission")
    jwt = JWTService()

    @classmethod
    async def has_permission(cls, user_id: str, action: Action, resource: Module):
        # implement user permission logic
        ...

    @classmethod
    async def has_permission(cls, action: Action, resource: Module):
        ...