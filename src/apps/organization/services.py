from bson import ObjectId
from bson.errors import InvalidId
from src.apps.organization.schemas import (
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
    OrganizationLoginSchema,
    OrganizationObjectSchema
)
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password, verify_password
from src.utilities.crypto.jwt import JWTService


class OrganizationService:
    jwt = JWTService()

    @classmethod
    async def get_collection(cls):
        return await get_collection("Organizations")
     

    # ---------------- CREATE ----------------
    @classmethod
    async def create(cls, dto: OrganizationCreateSchema):
        collection = await cls.get_collection()
        org_data = dto.dict()
        org_data["password"] = set_password(dto.password)
        result = await collection.insert_one(org_data)
        # fetch the inserted document
        org = await collection.find({"_id": result.inserted_id}).to_list(length=1)
        return OrganizationObjectSchema(**org[0])

    # ---------------- LOGIN ----------------
    @classmethod
    async def login_org(cls, dto: OrganizationLoginSchema):
        collection = await cls.get_collection()
        org = await collection.find({"email": dto.email}).to_list(length=1)
        if not org:
            return None
        org = org[0]
        if not verify_password(dto.password, org["password"]):
            return None
        return OrganizationObjectSchema(**org)

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
