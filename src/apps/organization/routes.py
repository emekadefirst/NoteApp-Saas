from fastapi import Depends, Response, Request, HTTPException
from src.utilities.route_builder import build_router
from src.dependencies.dependencies import PermissionDependency
from src.apps.organization.services import OrganizationService
from src.apps.organization.schemas import (
    OrganizationCreateSchema, 
    OrganizationUpdateSchema,
    OrganizationLoginSchema
)
from src.enums.base import Action, Module

organization_router = build_router(path="organizations", tags=["Organizations"])





@organization_router.get(
    path="",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.READ,
                resource=Module.ORGANIZATION
            )
        )
    ],
)
async def get_all_organization(request: Request):
    
    admin = getattr(request.state, "account", None)
    return await OrganizationService.get_all()





@organization_router.get("/whoami", status_code=200)
async def get_organization_profile(request: Request):
    """
    Returns the authenticated organization's profile.
    """
    account = getattr(request.state, "account", None)
    account_type = getattr(request.state, "account_type", None)

    if not account or account_type != "organization":
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await OrganizationService.get_by_id(org_id=str(account["_id"]))





@organization_router.get(
    path="/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.READ,
                resource=Module.ORGANIZATION
            )
        )
    ],
)
async def get_organization(id: str):
    return await OrganizationService.get_by_id(org_id=id)





@organization_router.post("", status_code=201)
async def create_organization(dto: OrganizationCreateSchema, response: Response):
    return await OrganizationService.create(dto=dto, response=response)





@organization_router.post("/login", status_code=200)
async def login_organization(dto: OrganizationLoginSchema, response: Response):
    return await OrganizationService.login_org(dto=dto, response=response)





@organization_router.patch(
    path="/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.UPDATE,
                resource=Module.ORGANIZATION
            )
        )
    ],
)
async def update_organization(id: str, dto: OrganizationUpdateSchema):
    return await OrganizationService.update(org_id=id, dto=dto)





@organization_router.delete(
    path="/{id}",
    status_code=204,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.DELETE,
                resource=Module.ORGANIZATION
            )
        )
    ],
)
async def delete_organization(id: str):
    return await OrganizationService.delete(org_id=id)
