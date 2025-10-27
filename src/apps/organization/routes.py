from fastapi import Depends, Response
from src.utilities.route_builder import build_router
from src.utilities.crypto.jwt import JWTService
from src.apps.organization.services import OrganizationService
from src.apps.organization.schemas import (
    OrganizationCreateSchema, 
    OrganizationUpdateSchema,
    OrganizationLoginSchema
)

jwt = JWTService()
organization_router = build_router(path="organizations", tags=["Organizations"])

@organization_router.get("", status_code=200)
async def get_all_organization():
    return await OrganizationService.get_all()

@organization_router.get("/whoami", status_code=200)
async def get_organization_profile(object_id: str = Depends(jwt.get_current_user)):
    return await OrganizationService.get_by_id(org_id=object_id)

@organization_router.get("/{id}", status_code=200)
async def get_organization(id: str):
    return await OrganizationService.get_by_id(org_id=id)


@organization_router.post("", status_code=201)
async def create_organization(dto: OrganizationCreateSchema, response: Response):
    return await OrganizationService.create(dto=dto, response=response)


@organization_router.post("/login", status_code=200)
async def login_organization(dto: OrganizationLoginSchema, response: Response):
    return await OrganizationService.login_org(dto=dto, response=response)



@organization_router.patch("/{id}", status_code=200)
async def update_organization(id: str, dto: OrganizationUpdateSchema):
    return await OrganizationService.update(org_id=id, dto=dto)

@organization_router.delete("/{id}", status_code=204)
async def delete_organization(id: str):
    return await OrganizationService.delete(org_id=id)