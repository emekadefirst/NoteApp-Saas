from fastapi import Depends, Request
from src.utilities.crypto.jwt import JWTService
from src.errors.base import ErrorHandler
from src.core.database import get_collection
from src.enums.base import AdminRole, Action, Module, OrganizationRole
from bson import ObjectId
from typing import Optional
from src.apps.admin.schemas import AdminObjectSchema
from src.apps.organization.schemas import OrganizationObjectSchema
from src.apps.user.schemas import UserObjectSchema


# -------------------------------------------------------------------
# BASE PERMISSION
# -------------------------------------------------------------------
class BasePermissionDependency:
    jwt = JWTService()
    error = ErrorHandler("Permission")

    @staticmethod
    def _safe_objectid(value):
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, dict) and "_id" in value:
            return ObjectId(value["_id"])
        return ObjectId(value)

    @staticmethod
    async def _resolve_account(user_data: dict):
        """
        Resolves JWT payload into a full object schema.
        """
        if not user_data:
            return None, None

        user_id = user_data.get("id")
        user_type = user_data.get("user_type")
        if not user_id or not user_type:
            return None, None

        if user_type == "admin":
            collection = await get_collection("Admins")
            admin = await collection.find_one({"_id": ObjectId(user_id)})
            return (AdminObjectSchema(**admin), "admin") if admin else (None, None)

        elif user_type == "organization":
            collection = await get_collection("Organizations")
            org = await collection.find_one({"_id": ObjectId(user_id)})
            return (OrganizationObjectSchema(**org), "organization") if org else (None, None)

        elif user_type == "user":
            collection = await get_collection("Users")
            user = await collection.find_one({"_id": ObjectId(user_id)})
            return (UserObjectSchema(**user), "user") if user else (None, None)

        return None, None


# -------------------------------------------------------------------
# ADMIN PERMISSIONS
# -------------------------------------------------------------------
class AdminPermissionDependency(BasePermissionDependency):
    error = ErrorHandler("Admin Permission")

    @classmethod
    async def has_permission(cls, admin: AdminObjectSchema, action: Action, resource: Module) -> bool:
        # Full access for system admins
        if admin.role == AdminRole.ADMIN:
            return True

        # Moderators: check group-based permissions
        if admin.role == AdminRole.MODERATOR:
            permission_group_collection = await get_collection("AdminPermissionGroups")
            permission_collection = await get_collection("AdminPermissions")

            group_ids = [cls._safe_objectid(g) for g in getattr(admin, "permission_groups", [])]
            if not group_ids:
                return False

            groups = await permission_group_collection.find({"_id": {"$in": group_ids}}).to_list(length=None)
            for group in groups:
                perm_ids = group.get("permissions", [])
                if not perm_ids:
                    continue
                perms = await permission_collection.find({"_id": {"$in": perm_ids}}).to_list(length=None)
                for perm in perms:
                    if perm.get("action") == action and perm.get("module") == resource:
                        return True
        return False


# -------------------------------------------------------------------
# ORGANIZATION + USER PERMISSIONS
# -------------------------------------------------------------------
class UserPermissionDependency(BasePermissionDependency):
    error = ErrorHandler("User Permission")

    @classmethod
    async def has_permission(
        cls,
        action: Action,
        resource: Module,
        user: Optional[UserObjectSchema] = None,
        organization: Optional[OrganizationObjectSchema] = None
    ) -> bool:
        # --- Organization Level ---
        if organization:
            # Organization can manage its own users and notes only
            if resource in [Module.USER, Module.NOTE]:
                return True
            return False

        # --- User Level ---
        if not user:
            return False

        # Base user can only access their own notes
        if getattr(user, "role", None) == OrganizationRole.BASE_USER:
            return resource == Module.NOTE

        # Moderators: check permissions
        if getattr(user, "role", None) == OrganizationRole.MODERATOR:
            permission_group_collection = await get_collection("UserPermissionGroups")
            permission_collection = await get_collection("UserPermissions")

            group_ids = [cls._safe_objectid(g) for g in getattr(user, "permission_groups", [])]
            if not group_ids:
                return False

            groups = await permission_group_collection.find({"_id": {"$in": group_ids}}).to_list(length=None)
            for group in groups:
                perm_ids = group.get("permissions", [])
                if not perm_ids:
                    continue
                perms = await permission_collection.find({"_id": {"$in": perm_ids}}).to_list(length=None)
                for perm in perms:
                    if perm.get("action") == action and perm.get("module") == resource:
                        return True
        return False


# -------------------------------------------------------------------
# UNIVERSAL WRAPPER
# -------------------------------------------------------------------
class PermissionDependency(BasePermissionDependency):
    error = ErrorHandler("Permission")

    @classmethod
    def permission_required(cls, action: Action, resource: Module):
        async def dependency(request: Request):
            account_data = getattr(request.state, "account", None)

            if not account_data:
                raise cls.error.get(401, "Authentication required or invalid token.")

            account, account_type = await cls._resolve_account(account_data)
            if not account:
                raise cls.error.get(401, "Unable to resolve account information.")

            # --- ADMIN ---
            if account_type == "admin":
                has_perm = await AdminPermissionDependency.has_permission(account, action, resource)
                if not has_perm:
                    raise cls.error.get(403, "Admin lacks permission for this action.")
                return account

            # --- ORGANIZATION ---
            if account_type == "organization":
                has_perm = await UserPermissionDependency.has_permission(action, resource, None, account)
                if not has_perm:
                    raise cls.error.get(403, "Organization lacks permission for this action.")
                return account

            # --- USER ---
            if account_type == "user":
                has_perm = await UserPermissionDependency.has_permission(action, resource, account)
                if not has_perm:
                    raise cls.error.get(403, "User lacks permission for this action.")
                return account

            raise cls.error.get(401, f"Unknown account type: {account_type}")

        return dependency
