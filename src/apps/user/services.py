from src.apps.user.schemas import (
    UserCreateSchema,
    UserObjectSchema,
    UserLoginSchema,
    UserUpdateSchema
)
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Response
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password, verify_password
from src.utilities.crypto.jwt import JWTService
from datetime import datetime
import pytz
from src.errors.base import ErrorHandler
from fastapi import Response, HTTPException, status
from datetime import datetime
from bson import ObjectId
import pytz
from src.enums.base import OrganizationRole


class UserService:
    token = JWTService()
    error = ErrorHandler("User")

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
            path="/"
        )

    @classmethod
    async def get_collection(cls):
        return await get_collection("Users")
    

    @classmethod
    async def login_org(cls, dto: UserLoginSchema, response: Response):
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
        data = {"id": str(org["_id"]), "user_type": "user"}
        tokens = cls.token.generate_token(data)   
        return cls._set_auth_cookies(response, tokens)

    # ---------------- CREATE ----------------

   

    @classmethod
    async def create(cls, dto: UserCreateSchema, response: Response, org_id: str | None = None):
        collection = await cls.get_collection()

        # Validate org_id only if provided
        if org_id:
            try:
                org_object_id = ObjectId(org_id)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid organization ID")

        # Check for existing email or phone number
        existing_user = await collection.find_one({
            "$or": [
                {"email": dto.email},
                {"phone_number": dto.phone_number}
            ]
        })

        if existing_user:
            if existing_user.get("email") == dto.email:
                raise cls.error.get(415, "Email already exists")
            if existing_user.get("phone_number") == dto.phone_number:
                raise cls.error.get(415, "Phone number already registered")

        # Prepare user data
        user_data = dto.dict(exclude_unset=True)
        user_data["password"] = set_password(dto.password) if dto.password else None

        lagos_tz = pytz.timezone("Africa/Lagos")
        user_data["created_at"] = datetime.now(lagos_tz)
        user_data["updated_at"] = None
        user_data["role"] = OrganizationRole.BASE_USER
        user_data["permission_groups"] = []

        # Only attach org_id if user belongs to an organization
        if org_id:
            user_data["organization_id"] = org_object_id

        result = await collection.insert_one(user_data)

        # Generate tokens
        data = {"id": str(result.inserted_id), "user_type": "user"}
        tokens = cls.token.generate_token(data)

        return cls._set_auth_cookies(response, tokens)


    # ---------------- GET BY ID ----------------
    @classmethod
    async def get_by_id(cls, user_id: str):
        try:
            _id = ObjectId(user_id)
        except InvalidId:
            return None
        collection = await cls.get_collection()
        org = await collection.find({"_id": _id}).to_list(length=1)
        if org:
            return UserObjectSchema(**org[0])
        return None
    
    @classmethod
    async def get_all(cls):
        collection = await cls.get_collection()
        docs = await collection.find({}).to_list(length=None)
        return [UserObjectSchema(**doc) for doc in docs]


    # ---------------- UPDATE ----------------
    @classmethod
    async def update(cls, user_id: str, dto: UserUpdateSchema):
        try:
            _id = ObjectId(user_id)
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
            return UserObjectSchema(**org[0])
        return None

    # ---------------- DELETE ----------------
    @classmethod
    async def delete(cls, user_id: str):
        try:
            _id = ObjectId(user_id)
        except InvalidId:
            return 0
        collection = await cls.get_collection()
        result = await collection.delete_one({"_id": _id})
        return result.deleted_count

