from fastapi import Depends, Request
from src.utilities.route_builder import build_router
from src.apps.permission.services.organization_permission_services import OrganizationPermissionService
from src.apps.permission.schemas.organization_permission_schemas import (
    OrganizationPermissionCreateSchema, OrganizationPermissionUpdateSchema
)
from src.dependencies.dependencies import PermissionDependency
from src.enums.base import Action, OrganizationModule

organization_permission_router = build_router(
    path="organization/permissions", tags=["Organization Permissions"]
)


@organization_permission_router.get(
    "",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.READ, resource=OrganizationModule.PERMISSION))],
)
async def get_all_permissions(request: Request):
    account = getattr(request.state, "account", None)
    account_type = getattr(request.state, "account_type", None)

    # Admins and Organization owners can view organization permissions
    if account_type not in ["organization", "admin"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Unauthorized access")

    org_id = account.get("_id") if account_type == "organization" else request.query_params.get("organization_id")
    return await OrganizationPermissionService.get_all(organization_id=str(org_id))


@organization_permission_router.post(
    "",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.CREATE, resource=OrganizationModule.PERMISSION))],
)
async def create_permission(dto: OrganizationPermissionCreateSchema, request: Request):
    account = getattr(request.state, "account", None)
    if getattr(request.state, "account_type", None) != "organization":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Only organizations can create permissions")
    return await OrganizationPermissionService.create(dto=dto, organization_id=str(account["_id"]))


@organization_permission_router.patch(
    "/{id}",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.UPDATE, resource=OrganizationModule.PERMISSION))],
)
async def update_permission(id: str, dto: OrganizationPermissionUpdateSchema):
    return await OrganizationPermissionService.update(id=id, dto=dto)


@organization_permission_router.delete(
    "/{id}",
    dependencies=[Depends(PermissionDependency.permission_required(action=Action.DELETE, resource=OrganizationModule.PERMISSION))],
)
async def delete_permission(id: str):
    return await OrganizationPermissionService.delete(id=id)
