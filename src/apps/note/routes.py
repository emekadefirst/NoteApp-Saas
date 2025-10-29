from bson import ObjectId
from fastapi import Depends, Request
from src.utilities.route_builder import build_router
from src.apps.note.services import NoteService
from src.apps.note.schemas import NoteCreateSchema, NoteUpdateSchema
from src.dependencies.dependencies import PermissionDependency
from src.enums.base import Action, OrganizationModule

note_router = build_router(path="notes", tags=["Notes"])


@note_router.get(
    path="",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.READ,
                resource=OrganizationModule.NOTE
            )
        )
    ],
)
async def get_all_notes():
    return await NoteService.get_all()


@note_router.get(
    path="/user",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.READ,
                resource=OrganizationModule.NOTE
            )
        )
    ],
)
async def get_user_notes(request: Request):
    """
    Fetch notes belonging to the currently authenticated user.
    """
    account = getattr(request.state, "account", None)
    account_type = getattr(request.state, "account_type", None)

    if not account or account_type not in ["user", "organization"]:
    
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized or invalid account type")

    return await NoteService.get_user(user_id=str(account["_id"]))


@note_router.get(
    path="/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.READ,
                resource=OrganizationModule.NOTE
            )
        )
    ],
)
async def get_note_by_id(id: str):
    return await NoteService.get_by_id(note_id=id)


@note_router.post(
    "",
    status_code=201,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.CREATE,
                resource=OrganizationModule.NOTE
            )
        )
    ],
)
async def create_note(dto: NoteCreateSchema, request: Request):
    """
    Create a note owned by the current user.
    """
    account = getattr(request.state, "account", None)
    account_type = getattr(request.state, "account_type", None)

    if not account or account_type != "user":
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Only users can create notes")

    dto.user_id = ObjectId(account["_id"])
    return await NoteService.create(dto=dto)


@note_router.patch(
    path="/{id}",
    status_code=200,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.UPDATE,
                resource=OrganizationModule.NOTE
            )
        )
    ],
)
async def update_note(id: str, dto: NoteUpdateSchema):
    return await NoteService.update(note_id=id, dto=dto)


@note_router.delete(
    path="/{id}",
    status_code=204,
    dependencies=[
        Depends(
            PermissionDependency.permission_required(
                action=Action.DELETE,
                resource=OrganizationModule.NOTE
            )
        )
    ],
)
async def delete_note(id: str):
    return await NoteService.delete(note_id=id)
