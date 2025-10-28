from fastapi import Response, Depends
from src.utilities.route_builder import build_router
from src.apps.admin.services import AdminService
from src.utilities.crypto.jwt import JWTService
from src.apps.admin.schemas import (
    AdminLoginSchema, 
    AdminObjectSchema, 
    AdminUserCreateSchema, 
    AdminUserUpdateSchema
)

jwt = JWTService()

admin_router = build_router(path="admin", tags=["Admin"])

@admin_router.post("/signup", status_code=201)
async def create_admin(dto: AdminUserCreateSchema, response: Response):
    return await AdminService.create(dto=dto, response=response)


@admin_router.post("/login", status_code=200)
async def login_admin(dto: AdminLoginSchema, response: Response):
    return await AdminService.login(dto=dto, response=response)

@admin_router.get("/whoami", status_code=200)
async def get_admin_detail(object_id: str = Depends(jwt.get_current_user)):
    return await AdminService.get_by_id(admin_id=object_id)

