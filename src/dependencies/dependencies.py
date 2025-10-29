from fastapi import Depends, Request
from src.utilities.crypto.jwt import JWTService
from src.errors.base import ErrorHandler
from src.apps.admin.schemas import AdminObjectSchema
from src.apps.organization.schemas import OrganizationObjectSchema
from src.apps.user.schemas import UserObjectSchema
from src.core.database import get_collection
from src.enums.base import AdminRole, Action, Module, OrganizationRole
from bson import ObjectId
from typing import Optional


class BasePermissionDependency:
    jwt = JWTService()
    error = ErrorHandler("Permission")

    @staticmethod
    async def _resolve_account(user_data: dict):
        """
        Resolves a minimal JWT payload (id, user_type)
        into a full object schema from the corresponding collection.
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
            return AdminObjectSchema(**admin) if admin else None, "admin"

        elif user_type == "organization":
            collection = await get_collection("Organizations")
            org = await collection.find_one({"_id": ObjectId(user_id)})
            return OrganizationObjectSchema(**org) if org else None, "organization"

        elif user_type == "user":
            collection = await get_collection("Users")
            user = await collection.find_one({"_id": ObjectId(user_id)})
            return UserObjectSchema(**user) if user else None, "user"

        return None, None


# -------------------------------------------------------------------
# ADMIN PERMISSION
# -------------------------------------------------------------------
class AdminPermissionDependency(BasePermissionDependency):
    error = ErrorHandler("Admin Permission")

    @classmethod
    async def has_permission(cls, user: AdminObjectSchema, action: Action, resource: Module) -> bool:
        if user.role == AdminRole.ADMIN:
            return True

        permission_group_collection = await get_collection("AdminPermissionGroups")
        permission_collection = await get_collection("AdminPermissions")

        group_ids = [ObjectId(g["_id"]) if isinstance(g, dict) else ObjectId(g) for g in user.permission_groups]

        groups_cursor = permission_group_collection.find({"_id": {"$in": group_ids}})
        groups = await groups_cursor.to_list(length=None)

        for group in groups:
            perm_ids = group.get("permissions", [])
            if not perm_ids:
                continue
            perms_cursor = permission_collection.find({"_id": {"$in": perm_ids}})
            perms = await perms_cursor.to_list(length=None)

            for perm in perms:
                if perm.get("action") == action and perm.get("module") == resource:
                    return True
        return False

    @classmethod
    def permission_required(cls, action: Action, resource: Module):
        async def dependency(user_data: dict = Depends(cls.jwt.get_current_user)):
            user, _ = await cls._resolve_account(user_data)
            if not user:
                raise cls.error.get(401, "Invalid or missing admin account.")
            has_perm = await cls.has_permission(user, action, resource)
            if not has_perm:
                raise cls.error.get(403, "You do not have permission to perform this action.")
            return user
        return dependency


# -------------------------------------------------------------------
# USER PERMISSION
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
        if organization:
            return True  # Organizations have full access

        if not user:
            return False

        if getattr(user, "role", None) == OrganizationRole.BASE_USER:
            return False

        if getattr(user, "role", None) == OrganizationRole.MODERATOR:
            permission_group_collection = await get_collection("AdminPermissionGroups")
            permission_collection = await get_collection("AdminPermissions")

            group_ids = [
                ObjectId(g["_id"]) if isinstance(g, dict) else ObjectId(g)
                for g in getattr(user, "permission_groups", [])
            ]
            if not group_ids:
                return False
            groups_cursor = permission_group_collection.find({"_id": {"$in": group_ids}})
            groups = await groups_cursor.to_list(length=None)
            for group in groups:
                perm_ids = group.get("permissions", [])
                if not perm_ids:
                    continue
                perms_cursor = permission_collection.find({"_id": {"$in": perm_ids}})
                perms = await perms_cursor.to_list(length=None)

                for perm in perms:
                    if perm.get("action") == action and perm.get("module") == resource:
                        return True
        return False

    @classmethod
    def permission_required(cls, action: Action, resource: Module):
        async def dependency(
            user_data: dict = Depends(cls.jwt.get_current_user),
            organization: Optional[OrganizationObjectSchema] = None
        ):
            user, user_type = await cls._resolve_account(user_data)
            has_perm = await cls.has_permission(action, resource, user, organization)
            if not has_perm:
                raise cls.error.get(403, "You do not have permission to perform this action.")
            return user or organization
        return dependency


# -------------------------------------------------------------------
# UNIVERSAL PERMISSION WRAPPER
# -------------------------------------------------------------------
class PermissionDependency(BasePermissionDependency):
    error = ErrorHandler("Permission")

    @classmethod
    def permission_required(cls, action: Action, resource: Module):
        async def dependency(request: Request):
            account_data = getattr(request.state, "account", None)
            account_type = getattr(request.state, "account_type", None)

            if not account_data or not account_type:
                raise cls.error.get(401, "Authentication required or invalid token.")

            account, _ = await cls._resolve_account(account_data)
            if not account:
                raise cls.error.get(401, "Unable to resolve account information.")

            if account_type == "admin":
                has_perm = await AdminPermissionDependency.has_permission(account, action, resource)
                if not has_perm:
                    raise cls.error.get(403, "Admin lacks permission for this action.")
                return account

            elif account_type == "organization":
                has_perm = await UserPermissionDependency.has_permission(action, resource, None, account)
                if not has_perm:
                    raise cls.error.get(403, "Organization lacks permission for this action.")
                return account

            elif account_type == "user":
                has_perm = await UserPermissionDependency.has_permission(action, resource, account)
                if not has_perm:
                    raise cls.error.get(403, "User lacks permission for this action.")
                return account

            raise cls.error.get(401, f"Unknown account type: {account_type}")
        return dependency
