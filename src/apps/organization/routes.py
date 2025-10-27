from src.utilities.route_builder import build_router
from src.apps.organization.services import OrganizationService
from src.apps.organization.schemas import (
    OrganizationCreateSchema, 
    OrganizationUpdateSchema,
    OrganizationLoginSchema
)



organization_router = build_router(path="organizations", tags=["Organizations"])

@organization_router.get("", status_code=200)
async def get_all_organization():
    return await OrganizationService.get_all()

@organization_router.get("/{id}", status_code=200)
async def get_organization(id: str):
    return await OrganizationService.get_by_id(id=id)


@organization_router.post("", status_code=201)
async def create_organization(dto: OrganizationCreateSchema):
    return await OrganizationService.create(dto=dto)