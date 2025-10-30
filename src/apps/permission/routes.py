from fastapi import Depends, Request
from src.utilities.route_builder import build_router
from src.apps.permission.services import PermissionService, PermissionGroupService
from src.apps.permission.schemas import PermissionObjectSchema, PermissionGroupObjectSchema
from src.dependencies.dependencies import PermissionControl
from src.enums.base import Action, Module
from bson import ObjectId

permission_router = build_router(path="permissions", tags=["Permissions"])


# ---------------- PERMISSION GROUPS ---------------- #
# (Static paths FIRST to avoid /{id} route conflicts)

@permission_router.get(
    path="/groups",
    status_code=200,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.READ,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def get_all_permission_groups():
    """Fetch all permission groups (with permissions expanded)."""
    return await PermissionGroupService.get_all()


@permission_router.get(
    path="/groups/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.READ,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def get_permission_group_by_id(id: str):
    """Fetch a single permission group by ID."""
    return await PermissionGroupService.get_by_id(group_id=id)


@permission_router.post(
    path="/groups",
    status_code=201,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.CREATE,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def create_permission_group(dto: PermissionGroupObjectSchema, request: Request):
    """Create a new permission group."""
    return await PermissionGroupService.create(data=dto.model_dump())


@permission_router.patch(
    path="/groups/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.UPDATE,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def update_permission_group(id: str, dto: PermissionGroupObjectSchema):
    """Update a permission group (not yet implemented in service)."""
    # Placeholder for future update logic
    return {"message": "Update functionality not implemented yet"}


@permission_router.delete(
    path="/groups/{id}",
    status_code=204,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.DELETE,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def delete_permission_group(id: str):
    """Delete a permission group."""
    return await PermissionGroupService.delete(group_id=id)


# ---------------- PERMISSIONS ---------------- #
# (Dynamic routes BELOW static ones)

@permission_router.get(
    path="",
    status_code=200,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.READ,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def get_all_permissions():
    """Fetch all permissions."""
    return await PermissionService.get_all()


@permission_router.get(
    path="/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.READ,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def get_permission_by_id(id: str):
    """Fetch a single permission by ID."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid permission ID")
    return await PermissionService.get_by_id(id=id)


@permission_router.post(
    path="",
    status_code=201,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.CREATE,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def create_permission(dto: PermissionObjectSchema, request: Request):
    """Create a new permission."""
    return await PermissionService.create(data=dto.model_dump())


@permission_router.delete(
    path="/{id}",
    status_code=204,
    dependencies=[
        Depends(
            PermissionControl.permission_required(
                action=Action.DELETE,
                resource=Module.PERMISSION,
            )
        )
    ],
)
async def delete_permission(id: str):
    """Delete a permission."""
    return await PermissionService.delete(permission_id=id)
