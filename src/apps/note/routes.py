from bson import ObjectId
from fastapi import Depends, Response
from src.utilities.route_builder import build_router
from src.utilities.crypto.jwt import JWTService
from src.apps.note.services import NoteService
from src.apps.note.schemas import NoteCreateSchema, NoteUpdateSchema

jwt = JWTService()
note_router = build_router(path="notes", tags=["Notes"])


@note_router.get("", status_code=200)
async def get_all_notes():
    return await NoteService.get_all()


@note_router.get("/user", status_code=200)
async def get_user_notes(object_id: str = Depends(jwt.get_current_user)):
    return await NoteService.get_user(user_id=object_id)


@note_router.get("/{id}", status_code=200)
async def get_note_by_id(id: str):
    return await NoteService.get_by_id(note_id=id)


@note_router.post("", status_code=201)
async def create_note(dto: NoteCreateSchema, object_id: str = Depends(jwt.get_current_user)):
    dto.user_id = ObjectId(object_id)  
    return await NoteService.create(dto=dto)


@note_router.patch("/{id}", status_code=200)
async def update_note(id: str, dto: NoteUpdateSchema):
    return await NoteService.update(note_id=id, dto=dto)


@note_router.delete("/{id}", status_code=204)
async def delete_note(id: str):
    return await NoteService.delete(note_id=id)
