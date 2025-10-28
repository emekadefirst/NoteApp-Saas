from fastapi import Depends
from src.utilities.crypto.jwt import JWTService
from src.errors.base import ErrorHandler
from src.apps.admin.schemas import AdminObjectSchema
from src.apps.organization.schemas import OrganizationObjectSchema
from src.apps.user.schemas import UserObjectSchema
from src.core.database import get_collection
from src.enums.base import AdminRole, Action, Module, OrganizationModule, OrganizationRole
from bson import ObjectId
from typing import Optional

class AdminPermissionDependency:
    error = ErrorHandler("Admin Permission")
    jwt = JWTService()

    @classmethod
    async def has_permission(cls, user: AdminObjectSchema, action: Action, resource: Module) -> bool:
        """
        Checks if the admin user has permission to perform a given action on a resource.
        """

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
        """
        Returns a FastAPI dependency that ensures the current admin user has the specified permission.
        """

        async def dependency(user: AdminObjectSchema = Depends(cls.jwt.get_current_user)):
            has_perm = await cls.has_permission(user, action, resource)
            if not has_perm:
                raise cls.error.get(403, "You do not have permission to perform this action.")
            return user

        return dependency


class UserPermissionDepency:
    error = ErrorHandler("User Permission")
    jwt = JWTService()

    @classmethod
    async def has_permission(cls, action: Action, resource: Module, user: Optional[UserObjectSchema] = None, organization: Optional[OrganizationObjectSchema] = None) -> bool:
        """
        Checks if the admin user has permission to perform a given action on a resource.
        """
        if organization:
            return True
        if user == None:
            if user.role == OrganizationRole.MODERATOR:
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
        """
        Returns a FastAPI dependency that ensures the current admin user has the specified permission.
        """
        async def dependency(user: AdminObjectSchema = Depends(cls.jwt.get_current_user)):
            has_perm = await cls.has_permission(user, action, resource)
            if not has_perm:
                raise cls.error.get(403, "You do not have permission to perform this action.")
            return user

        return dependency
    


class UserPermissionDependency:
    error = ErrorHandler("User Permission")
    jwt = JWTService()

    @classmethod
    async def has_permission(
        cls,
        action: Action,
        resource: Module,
        user: Optional[UserObjectSchema] = None,
        organization: Optional[OrganizationObjectSchema] = None
    ) -> bool:
        """
        Checks if the user (or organization) has permission to perform a given action on a resource.
        """

        if organization:
            return True

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
        """
        Returns a FastAPI dependency that ensures the current user or organization
        has the specified permission.
        """
        async def dependency(
            user: UserObjectSchema = Depends(cls.jwt.get_current_user),
            organization: Optional[OrganizationObjectSchema] = None
        ):
            has_perm = await cls.has_permission(action, resource, user, organization)
            if not has_perm:
                raise cls.error.get(403, "You do not have permission to perform this action.")
            return user or organization

        return dependency
