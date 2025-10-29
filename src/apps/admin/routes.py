from fastapi import Response, Depends, Request, HTTPException
from src.utilities.route_builder import build_router
from src.apps.admin.services import AdminService
from src.apps.admin.schemas import (
    AdminLoginSchema, 
    AdminUserCreateSchema, 
    AdminUserUpdateSchema
)
from src.dependencies.dependencies import AdminPermissionDependency
from src.enums.base import Action, Module

admin_router = build_router(path="admin", tags=["Admin"])

@admin_router.post("/signup", status_code=201)
async def create_admin(dto: AdminUserCreateSchema, response: Response):
    return await AdminService.create(dto=dto, response=response)


@admin_router.post("/login", status_code=200)
async def login_admin(dto: AdminLoginSchema, response: Response):
    return await AdminService.login(dto=dto, response=response)


@admin_router.get(
    "/whoami",
    status_code=200,
    dependencies=[
        Depends(
            AdminPermissionDependency.permission_required(
                action=Action.READ,
                resource=Module.ADMIN
            )
        )
    ],
)
async def get_admin_detail(request: Request):
    """
    Returns the authenticated admin's details.
    """
    account = getattr(request.state, "account", None)
    account_type = getattr(request.state, "account_type", None)

    if not account or account_type != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized or invalid account type")

    return await AdminService.get_by_id(admin_id=str(account["_id"]))

@admin_router.patch(
    "/{id}",
    status_code=200,
    dependencies=[
        Depends(
            AdminPermissionDependency.permission_required(
                action=Action.UPDATE,
                resource=Module.ADMIN
            )
        )
    ],
)
async def update_admin(id: str, dto: AdminUserUpdateSchema):
    return await AdminService.update(admin_id=id, dto=dto)

@admin_router.delete(
    "/{id}",
    status_code=204,
    dependencies=[
        Depends(
            AdminPermissionDependency.permission_required(
                action=Action.DELETE,
                resource=Module.ADMIN
            )
        )
    ],
)
async def delete_admin(id: str):
    return await AdminService.delete(admin_id=id)
