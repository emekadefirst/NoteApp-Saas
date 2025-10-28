import asyncio
from datetime import datetime
import pytz
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password
from src.errors.base import ErrorHandler
from src.enums.base import AdminRole
from src.configs.env import (
    ADMIN_EMAIL,
    ADMIN_FIRSTNAME,
    ADMIN_LASTNAME,
    ADMIN_PASSWORD,
    ADMIN_PHONENUMBER,
)

lagos_tz = pytz.timezone("Africa/Lagos")

data = {
    "first_name": ADMIN_FIRSTNAME,
    "last_name": ADMIN_LASTNAME,
    "email": ADMIN_EMAIL,
    "role": AdminRole.ADMIN,
    "phone_number": ADMIN_PHONENUMBER,
    "password": set_password(ADMIN_PASSWORD),
    "permission_groups": [],
    "created_at": datetime.now(lagos_tz),
    "updated_at": None
}

error_handler = ErrorHandler("Admin")


async def get_admin_collection():
    """Return the MongoDB collection for admins."""
    return await get_collection("Admin")


async def create_admin():
    """Create a new admin user if not existing."""
    collection = await get_admin_collection()
    try:
        existing = await collection.find_one(
            {
                "$or": [
                    {"email": ADMIN_EMAIL},
                    {"phone_number": ADMIN_PHONENUMBER},
                ]
            }
        )

        if existing:
            raise error_handler.get(409)  

        result = await collection.insert_one(data)
        print("✅ Admin created")
        return result

    except Exception as exc:
        raise ValueError(f"Unknown error occurred while creating admin: {exc}")


def seed():
    return asyncio.run(create_admin())


