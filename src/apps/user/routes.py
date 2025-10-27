from fastapi import Depends, Response
from src.utilities.route_builder import build_router
from src.utilities.crypto.jwt import JWTService
from src.apps.user.services import UserService
from src.apps.user.schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserLoginSchema,
)

jwt = JWTService()
user_router = build_router(path="users", tags=["Users"])


# ---------------- GET ALL ----------------
@user_router.get("", status_code=200)
async def get_all_users():
    return await UserService.get_all()


# ---------------- WHOAMI ----------------
@user_router.get("/whoami", status_code=200)
async def get_user_profile(object_id: str = Depends(jwt.get_current_user)):
    return await UserService.get_by_id(user_id=object_id)


# ---------------- GET BY ID ----------------
@user_router.get("/{id}", status_code=200)
async def get_user(id: str):
    return await UserService.get_by_id(user_id=id)


# ---------------- CREATE ----------------
@user_router.post("", status_code=201)
async def create_user(dto: UserCreateSchema, response: Response, org_id: str = Depends(jwt.get_current_user)):
    return await UserService.create(dto=dto, response=response, org_id=org_id)


# ---------------- LOGIN ----------------
@user_router.post("/login", status_code=200)
async def login_user(dto: UserLoginSchema, response: Response):
    return await UserService.login_org(dto=dto, response=response)


# ---------------- UPDATE ----------------
@user_router.patch("/{id}", status_code=200)
async def update_user(id: str, dto: UserUpdateSchema):
    return await UserService.update(user_id=id, dto=dto)


# ---------------- DELETE ----------------
@user_router.delete("/{id}", status_code=204)
async def delete_user(id: str):
    return await UserService.delete(user_id=id)
