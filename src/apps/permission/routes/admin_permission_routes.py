from fastapi import Depends, Request
from src.utilities.route_builder import build_router
from src.apps.permission.services.admin_permission_services import AdminPermissionService
from src.apps.permission.schemas.admin_permission_schemas import (
    AdminPermissionCreateSchema, AdminPermissionUpdateSchema
)
from src.dependencies.dependencies import PermissionDependency
from src.enums.base import Action, Module

admin_permission_router = build_router(path="admin/permissions", tags=["Admin Permissions"])


@admin_permission_router.get(
    "",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.READ, resource=Module.PERMISSION))],
)
async def get_all_permissions():
    return await AdminPermissionService.get_all()


@admin_permission_router.post(
    "",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.CREATE, resource=Module.PERMISSION))],
)
async def create_permission(dto: AdminPermissionCreateSchema):
    return await AdminPermissionService.create(dto=dto)


@admin_permission_router.patch(
    "/{id}",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.UPDATE, resource=Module.PERMISSION))],
)
async def update_permission(id: str, dto: AdminPermissionUpdateSchema):
    return await AdminPermissionService.update(id=id, dto=dto)


@admin_permission_router.delete(
    "/{id}",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.DELETE, resource=Module.PERMISSION))],
)
async def delete_permission(id: str):
    return await AdminPermissionService.delete(id=id)
