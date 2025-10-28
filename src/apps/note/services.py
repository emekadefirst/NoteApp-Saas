from src.apps.note.schemas import (
    NoteCreateSchema,
    NoteUpdateSchema,
    NoteObjectSchema,
)
from src.errors.base import ErrorHandler
from src.core.database import get_collection
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId


class NoteService:
    error = ErrorHandler("Note")

    @classmethod
    async def get_collection(cls):
        return await get_collection("Notes")

    @classmethod
    async def create(cls, dto: NoteCreateSchema):
        collection = await cls.get_collection()
        note_data = dto.dict(exclude_unset=True)
        note_data["created_at"] = datetime.utcnow()
        note_data["updated_at"] = None
        

        result = await collection.insert_one(note_data)
        created = await collection.find_one({"_id": result.inserted_id})
        return NoteObjectSchema(**created)


    @classmethod
    async def get_all(cls):
        collection = await cls.get_collection()
        notes = await collection.find({}).to_list(length=None)
        return [NoteObjectSchema(**note) for note in notes]


    @classmethod
    async def get_user(cls, user_id: str):
        try:
            _id = ObjectId(user_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid user ID")

        collection = await cls.get_collection()
        docs = await collection.find({"user_id": _id}).to_list(length=None)
        return [NoteObjectSchema(**doc) for doc in docs]

  
    @classmethod
    async def get_by_id(cls, note_id: str):
        try:
            _id = ObjectId(note_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid note ID")

        collection = await cls.get_collection()
        note = await collection.find_one({"_id": _id})
        if not note:
            raise cls.error.get(404, "Note not found")
        return NoteObjectSchema(**note)


    @classmethod
    async def update(cls, note_id: str, dto: NoteUpdateSchema):
        try:
            _id = ObjectId(note_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid note ID")

        collection = await cls.get_collection()
        update_data = dto.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        result = await collection.update_one({"_id": _id}, {"$set": update_data})
        if result.modified_count == 0:
            raise cls.error.get(404, "Note not found or no changes made")

        note = await collection.find_one({"_id": _id})
        return NoteObjectSchema(**note)

 
    @classmethod
    async def delete(cls, note_id: str):
        try:
            _id = ObjectId(note_id)
        except InvalidId:
            raise cls.error.get(400, "Invalid note ID")

        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": _id})
        if result.deleted_count == 0:
            raise cls.error.get(404, "Note not found")

        return {"message": "Note deleted successfully"}
