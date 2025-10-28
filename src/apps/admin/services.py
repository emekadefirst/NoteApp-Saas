from bson import ObjectId
from bson.errors import InvalidId
from src.apps.admin.schemas import (
    AdminUserCreateSchema,
    AdminLoginSchema,
    AdminUserUpdateSchema,
    AdminObjectSchema
)
from src.errors.base import ErrorHandler
from fastapi import Response, HTTPException, status
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password, verify_password
from src.utilities.crypto.jwt import JWTService
from datetime import datetime
import pytz
from src.enums.base import AdminRole


class AdminService:
    token = JWTService()
    error = ErrorHandler("AdminUser")

    @staticmethod
    def _set_auth_cookies(response: Response, tokens: dict):
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="none",
            max_age=900,  
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="none",
            max_age=604800,  # 7 days
            path="/"
        )

    @classmethod
    async def get_collection(cls):
        return await get_collection("Admin")


    @classmethod
    async def login(cls, dto: AdminLoginSchema, response: Response):
        collection = await cls.get_collection()
        org = await collection.find_one({"email": dto.email})
        if not org:
            raise cls.error.get(400)

        if not verify_password(plain_password=dto.password, hashed_password=org["password"]):
            raise cls.error.get(400)
        lagos_tz = pytz.timezone("Africa/Lagos")
        await collection.update_one(
            {"_id": org["_id"]},
            {"$set": {"last_login": datetime.now(lagos_tz)}}
        )
        tokens = cls.token.generate_token(str(org["_id"]))
        return cls._set_auth_cookies(response, tokens)

    # ---------------- CREATE ----------------
    @classmethod
    async def create(cls, dto: AdminUserCreateSchema, response: Response):
        collection = await cls.get_collection()
        existing = await collection.find_one({
            "$or": [
                {"email": dto.email},
                {"phone_number": dto.phone_number}
            ]
        })

        if existing:
            raise cls.error.get(409)

        admin_data = dto.dict(exclude_unset=True)
        admin_data["password"] = set_password(dto.password)

        lagos_tz = pytz.timezone("Africa/Lagos")
        admin_data["created_at"] = datetime.now(lagos_tz)
        admin_data["updated_at"] = None
        admin_data["role"] = AdminRole.MODERATOR
        admin_data["permission_groups"] = []
        result = await collection.insert_one(admin_data)
        tokens = cls.token.generate_token(str(result.inserted_id))
        return cls._set_auth_cookies(response, tokens)

   
    @classmethod
    async def get_by_id(cls, admin_id: str):
        try:
            _id = ObjectId(admin_id)
        except InvalidId:
            return None
        collection = await cls.get_collection()
        org = await collection.find({"_id": _id}).to_list(length=1)
        if org:
            return AdminObjectSchema(**org[0])
        return None
    
    @classmethod
    async def get_all(cls):
        collection = await cls.get_collection()
        docs = await collection.find({}).to_list(length=None)
        return [AdminObjectSchema(**doc) for doc in docs]
    

    @classmethod
    async def update(cls, org_id: str, dto: AdminUserUpdateSchema):
        try:
            _id = ObjectId(org_id)
        except InvalidId:
            return None

        collection = await cls.get_collection()
        update_data = dto.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = set_password(update_data["password"])

        result = await collection.update_one(
            {"_id": _id},
            {"$set": update_data}
        )

        if result.modified_count:
            org = await collection.find({"_id": _id}).to_list(length=1)
            return AdminObjectSchema(**org[0])
        return None

    # ---------------- DELETE ----------------
    @classmethod
    async def delete(cls, org_id: str):
        try:
            _id = ObjectId(org_id)
        except InvalidId:
            return 0
        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": _id})
        return result.deleted_count
