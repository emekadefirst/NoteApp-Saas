from fastapi import Depends, Request, Response, HTTPException
from src.utilities.route_builder import build_router
from src.apps.user.services import UserService
from src.apps.user.schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserLoginSchema,
)
from src.dependencies.dependencies import UserPermissionDependency
from src.enums.base import Action, OrganizationModule

user_router = build_router(path="users", tags=["Users"])





@user_router.get(
    path="",
    status_code=200,
    dependencies=[Depends(UserPermissionDependency.permission_required(
        action=Action.READ, resource=OrganizationModule.USER
    ))],
)
async def get_all_users(request: Request):
    """
    Fetch all users (permission controlled)
    """
    
    account = getattr(request.state, "account", None)
    return await UserService.get_all()





@user_router.get("/whoami", status_code=200)
async def get_user_profile(request: Request):
    account = getattr(request.state, "account", None)
    if not account:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await UserService.get_by_id(user_id=str(account["_id"]))





@user_router.get(
    path="/{id}",
    status_code=200,
    dependencies=[Depends(UserPermissionDependency.permission_required(
        action=Action.READ, resource=OrganizationModule.USER
    ))],
)
async def get_user(id: str):
    return await UserService.get_by_id(user_id=id)





@user_router.post("", status_code=201)
async def create_user(
    dto: UserCreateSchema,
    response: Response,
    request: Request,
):
    account = getattr(request.state, "account", None)
    if not account:
        raise HTTPException(status_code=401, detail="Unauthorized")

    org_id = str(account["_id"]) if request.state.account_type == "organization" else None
    return await UserService.create(dto=dto, response=response, org_id=org_id)





@user_router.post("/login", status_code=200)
async def login_user(dto: UserLoginSchema, response: Response):
    return await UserService.login_org(dto=dto, response=response)





@user_router.patch(
    path="/{id}",
    status_code=200,
    dependencies=[Depends(UserPermissionDependency.permission_required(
        action=Action.UPDATE, resource=OrganizationModule.USER
    ))],
)
async def update_user(id: str, dto: UserUpdateSchema):
    return await UserService.update(user_id=id, dto=dto)





@user_router.delete(
    path="/{id}",
    status_code=204,
    dependencies=[Depends(UserPermissionDependency.permission_required(
        action=Action.DELETE, resource=OrganizationModule.USER
    ))],
)
async def delete_user(id: str):
    return await UserService.delete(user_id=id)
