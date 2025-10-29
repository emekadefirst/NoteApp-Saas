from bson import ObjectId
from bson.errors import InvalidId
from src.apps.organization.schemas import (
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
    OrganizationLoginSchema,
    OrganizationObjectSchema
)
from src.errors.base import ErrorHandler
from fastapi import Response, HTTPException, status
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password, verify_password
from src.utilities.crypto.jwt import JWTService
from datetime import datetime
import pytz


class OrganizationService:
    token = JWTService()
    error = ErrorHandler("Organization")

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
        return await get_collection("Organizations")


    @classmethod
    async def login_org(cls, dto: OrganizationLoginSchema, response: Response):
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
        data = {"id": str(org["_id"]), "user_type": "organization"}
        tokens = cls.token.generate_token(data)
        return cls._set_auth_cookies(response, tokens)

    # ---------------- CREATE ----------------
    @classmethod
    async def create(cls, dto: OrganizationCreateSchema, response: Response):
        collection = await cls.get_collection()
        existing = await collection.find_one({
            "$or": [
                {"email": dto.email},
                {"name": dto.name},
                {"phone_number": dto.phone_number}
            ]
        })

        if existing:
            raise cls.error.get(409)

        org_data = dto.dict(exclude_unset=True)
        org_data["password"] = set_password(dto.password)

        lagos_tz = pytz.timezone("Africa/Lagos")
        org_data["created_at"] = datetime.now(lagos_tz)
        org_data["updated_at"] = None
        result = await collection.insert_one(org_data)
        data = {"id": str(result.inserted_id), "user_type": "organization"}
        tokens = cls.token.generate_token(data)
        return cls._set_auth_cookies(response, tokens)

   


    # ---------------- GET BY ID ----------------
    @classmethod
    async def get_by_id(cls, org_id: str):
        try:
            _id = ObjectId(org_id)
        except InvalidId:
            return None
        collection = await cls.get_collection()
        org = await collection.find({"_id": _id}).to_list(length=1)
        if org:
            return OrganizationObjectSchema(**org[0])
        return None
    
    @classmethod
    async def get_all(cls):
        collection = await cls.get_collection()
        docs = await collection.find({}).to_list(length=None)
        return [OrganizationObjectSchema(**doc) for doc in docs]


    # ---------------- UPDATE ----------------
    @classmethod
    async def update(cls, org_id: str, dto: OrganizationUpdateSchema):
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
            return OrganizationObjectSchema(**org[0])
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
