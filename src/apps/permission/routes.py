from bson import ObjectId
from fastapi import Depends, Request, HTTPException
from typing import Optional

from src.utilities.route_builder import build_router
from src.apps.permission.services import PermissionService, PermissionGroupService
from src.apps.permission.schemas import (
    PermissionObjectSchema,
    PermissionGroupObjectSchema,
)
from src.dependencies.dependencies import PermissionControl
from src.enums.base import Action, Module

permission_router = build_router(path="permissions", tags=["Permissions"])


# ---------------- PERMISSIONS ---------------- #

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
    return await PermissionService.create(dto=dto)


@permission_router.patch(
    path="/{id}",
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
async def update_permission(id: str, dto: PermissionObjectSchema):
    return await PermissionService.update(permission_id=id, dto=dto)


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
    return await PermissionService.delete(permission_id=id)


# ---------------- PERMISSION GROUPS ---------------- #

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
    return await PermissionGroupService.create(dto=dto)


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
    return await PermissionGroupService.update(group_id=id, dto=dto)


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
    return await PermissionGroupService.delete(group_id=id)
