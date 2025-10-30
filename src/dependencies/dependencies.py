from fastapi import Request, Depends, HTTPException
from src.errors.base import ErrorHandler
from src.enums.base import Action, Module, AdminRole
from src.apps.admin.services import AdminService
from src.apps.user.services import UserService
from src.apps.organization.services import OrganizationService
from src.core.database import get_collection
from bson import ObjectId
from bson.errors import InvalidId


class AdminPermissionDependency:
    error = ErrorHandler("AdminPermission")

    @classmethod
    async def has_permission(cls, user_id: str, action: Action, resource: Module) -> bool:
        """
        Checks if an admin user has permission to perform an action on a module.
        Super admins automatically have all permissions.
        """
        try:
            admin_collection = await get_collection("Admin")
            admin = await admin_collection.find_one({"_id": ObjectId(user_id)})

            if not admin:
                raise cls.error.get(404, "Admin not found")

            # If admin has global privileges (super admin)
            if admin.get("role", AdminRole.ADMIN):
                return True

            # Check group-based permissions
            permission_group_ids = admin.get("permission_groups", [])
            if not permission_group_ids:
                return False

            group_collection = await get_collection("PermissionGroup")
            permission_collection = await get_collection("Permission")

            groups = await group_collection.find({
                "_id": {"$in": [ObjectId(g) for g in permission_group_ids]}
            }).to_list(None)

            for group in groups:
                perms = await permission_collection.find({
                    "_id": {"$in": [ObjectId(p) for p in group.get("permissions", [])]},
                    "action": action,
                    "module": resource
                }).to_list(None)
                if perms:
                    return True

            return False

        except InvalidId:
            raise cls.error.get(400, "Invalid admin ID")


class OrganizationPermissionDependency:
    error = ErrorHandler("OrganizationPermission")

    @classmethod
    async def has_permission(cls, user_id: str, action: Action, resource: Module) -> bool:
        """
        Checks if an organization account has permission.
        If the organization is a moderator-level account, it checks group-based permissions.
        """
        try:
            org_collection = await get_collection("Organization")
            organization = await org_collection.find_one({"_id": ObjectId(user_id)})

            if not organization:
                raise cls.error.get(404, "Organization not found")

            # Organization owners have full access
            if organization.get("role") == "owner":
                return True

            permission_group_ids = organization.get("permission_groups", [])
            if not permission_group_ids:
                return False

            group_collection = await get_collection("PermissionGroup")
            permission_collection = await get_collection("Permission")

            groups = await group_collection.find({
                "_id": {"$in": [ObjectId(g) for g in permission_group_ids]}
            }).to_list(None)

            for group in groups:
                perms = await permission_collection.find({
                    "_id": {"$in": [ObjectId(p) for p in group.get("permissions", [])]},
                    "action": action,
                    "module": resource
                }).to_list(None)
                if perms:
                    return True

            return False

        except InvalidId:
            raise cls.error.get(400, "Invalid organization ID")


class UserPermissionDependency:
    error = ErrorHandler("UserPermission")

    @classmethod
    async def has_permission(cls, user_id: str, action: Action, resource: Module) -> bool:
        """
        Checks if a base user has permission.
        Only users with attached permission groups can have permissions.
        """
        try:
            user_collection = await get_collection("User")
            user = await user_collection.find_one({"_id": ObjectId(user_id)})

            if not user:
                raise cls.error.get(404, "User not found")

            # Base users without permission groups cannot access
            permission_group_ids = user.get("permission_groups", [])
            if not permission_group_ids:
                return False

            group_collection = await get_collection("PermissionGroup")
            permission_collection = await get_collection("Permission")

            groups = await group_collection.find({
                "_id": {"$in": [ObjectId(g) for g in permission_group_ids]}
            }).to_list(None)

            for group in groups:
                perms = await permission_collection.find({
                    "_id": {"$in": [ObjectId(p) for p in group.get("permissions", [])]},
                    "action": action,
                    "module": resource
                }).to_list(None)
                if perms:
                    return True

            return False

        except InvalidId:
            raise cls.error.get(400, "Invalid user ID")



class PermissionControl:
    error = ErrorHandler("PermissionControl")

    @classmethod
    async def validate_permission(cls, request: Request, action: Action, resource: Module):
        """
        Determines if the current authenticated account has the given permission.
        The middleware must set request.state.user_type and request.state.user_id.
        """
        user_type = getattr(request.state, "user_type", None)
        user_id = getattr(request.state, "user_id", None)

        if not user_id or not user_type:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # ---------------- ADMIN ----------------
        if user_type == "admin":
            admin = await AdminService.get_by_id(user_id)
            if not admin:
                raise HTTPException(status_code=404, detail="Admin not found")

            # ✅ Ensure this matches your admin structure (e.g. admin["role"] == "admin")
            if admin.role == "admin":
                return True  # full access for admin
            else:
                raise HTTPException(status_code=403, detail="Forbidden: invalid admin role")

        elif user_type == "organization":
            has_permission = await OrganizationPermissionDependency.has_permission(
                user_id=user_id, action=action, resource=resource
            )

        # ---------------- USER ----------------
        elif user_type == "user":
            has_permission = await UserPermissionDependency.has_permission(
                user_id=user_id, action=action, resource=resource
            )

        else:
            raise HTTPException(status_code=403, detail="Invalid user type")

        if not has_permission:
            raise HTTPException(status_code=403, detail="Permission denied")

        return True

    # ---------------- ROUTE DECORATOR ----------------
    @classmethod
    def permission_required(cls, action: Action, resource: Module):
        """
        Usage:
            @router.get(
                "/notes",
                dependencies=[Depends(PermissionControl.permission_required(Action.READ, Module.NOTE))]
            )
        """
        async def dependency(request: Request):
            await cls.validate_permission(request, action, resource)

        return dependency
