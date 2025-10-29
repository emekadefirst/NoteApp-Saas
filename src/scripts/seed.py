import asyncio
from datetime import datetime
import pytz
from bson import ObjectId
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password
from src.errors.base import ErrorHandler
from src.enums.base import AdminRole, Action, Module, OrganizationModule
from src.configs.env import (
    ADMIN_EMAIL,
    ADMIN_FIRSTNAME,
    ADMIN_LASTNAME,
    ADMIN_PASSWORD,
    ADMIN_PHONENUMBER,
)

lagos_tz = pytz.timezone("Africa/Lagos")
error_handler = ErrorHandler("Seed")

# -------------------- DEFAULT ADMIN DATA --------------------
admin_data = {
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

# -------------------- ADMIN PERMISSIONS --------------------
def get_admin_permissions():
    """Generate all admin permissions based on Module and Action enums."""
    return [
        {
            "module": module.value,
            "action": action.value,
            "created_at": datetime.now(lagos_tz),
            "updated_at": None
        }
        for module in Module
        for action in Action
    ]

# -------------------- ORGANIZATION PERMISSIONS --------------------
def get_org_permissions():
    """Generate all organization permissions based on OrganizationModule and Action enums."""
    return [
        {
            "module": module.value,
            "action": action.value,
            "created_at": datetime.now(lagos_tz),
            "updated_at": None
        }
        for module in OrganizationModule
        for action in Action
    ]


# -------------------- GET COLLECTIONS --------------------
async def get_collections():
    return {
        "admins": await get_collection("Admins"),
        "admin_permissions": await get_collection("AdminPermissions"),
        "admin_permission_groups": await get_collection("AdminPermissionGroups"),
        "org_permissions": await get_collection("OrganizationPermissions"),
        "org_permission_groups": await get_collection("OrganizationPermissionGroups"),
        "organizations": await get_collection("Organizations"),
    }


# -------------------- CREATE ADMIN --------------------
async def create_admin(collections):
    admin_col = collections["admins"]

    existing = await admin_col.find_one({
        "$or": [{"email": ADMIN_EMAIL}, {"phone_number": ADMIN_PHONENUMBER}]
    })
    if existing:
        print("ℹ️ Admin already exists.")
        return existing

    result = await admin_col.insert_one(admin_data)
    print("✅ Admin created successfully.")
    return await admin_col.find_one({"_id": result.inserted_id})


# -------------------- CREATE ADMIN PERMISSIONS --------------------
async def create_admin_permissions(collections):
    perm_col = collections["admin_permissions"]
    existing_count = await perm_col.count_documents({})
    if existing_count > 0:
        print("ℹ️ Admin permissions already exist.")
        return await perm_col.find({}).to_list(length=None)

    permissions = get_admin_permissions()
    await perm_col.insert_many(permissions)
    print(f"✅ {len(permissions)} Admin permissions created.")
    return await perm_col.find({}).to_list(length=None)


# -------------------- CREATE ADMIN PERMISSION GROUP --------------------
async def create_admin_permission_group(collections, permissions, admin):
    group_col = collections["admin_permission_groups"]
    existing = await group_col.find_one({"name": "SuperAdminGroup"})
    if existing:
        print("ℹ️ SuperAdminGroup already exists.")
        return existing

    group_data = {
        "name": "SuperAdminGroup",
        "permissions": [perm["_id"] for perm in permissions],
        "created_at": datetime.now(lagos_tz),
        "updated_at": None
    }

    result = await group_col.insert_one(group_data)

    # Attach to admin
    admin_col = collections["admins"]
    await admin_col.update_one(
        {"_id": admin["_id"]},
        {"$set": {"permission_groups": [result.inserted_id]}}
    )

    print("✅ SuperAdminGroup created and assigned to admin.")
    return await group_col.find_one({"_id": result.inserted_id})


# -------------------- CREATE ORGANIZATION PERMISSIONS --------------------
async def create_org_permissions(collections):
    perm_col = collections["org_permissions"]
    existing_count = await perm_col.count_documents({})
    if existing_count > 0:
        print("ℹ️ Organization permissions already exist.")
        return await perm_col.find({}).to_list(length=None)

    permissions = get_org_permissions()
    await perm_col.insert_many(permissions)
    print(f"✅ {len(permissions)} Organization permissions created.")
    return await perm_col.find({}).to_list(length=None)


# -------------------- CREATE ORGANIZATION PERMISSION GROUPS --------------------
async def create_org_permission_groups(collections, permissions):
    group_col = collections["org_permission_groups"]

    existing_groups = await group_col.count_documents({})
    if existing_groups > 0:
        print("ℹ️ Organization permission groups already exist.")
        return await group_col.find({}).to_list(length=None)

    # Moderator has all permissions
    moderator_group = {
        "name": "ModeratorGroup",
        "permissions": [perm["_id"] for perm in permissions],
        "created_at": datetime.now(lagos_tz),
        "updated_at": None
    }

    # Base user has only READ permissions
    read_only_perms = [
        perm["_id"] for perm in permissions if perm["action"] == Action.READ.value
    ]
    base_user_group = {
        "name": "BaseUserGroup",
        "permissions": read_only_perms,
        "created_at": datetime.now(lagos_tz),
        "updated_at": None
    }

    await group_col.insert_many([moderator_group, base_user_group])
    print("✅ Organization permission groups (ModeratorGroup, BaseUserGroup) created.")

    return await group_col.find({}).to_list(length=None)


# -------------------- SEED RUNNER --------------------
async def run_seed():
    collections = await get_collections()

    # Step 1: Create Admin + Admin Permissions + Groups
    admin = await create_admin(collections)
    admin_permissions = await create_admin_permissions(collections)
    await create_admin_permission_group(collections, admin_permissions, admin)

    # Step 2: Create Organization Permissions + Groups
    org_permissions = await create_org_permissions(collections)
    await create_org_permission_groups(collections, org_permissions)

    print("🎉 Seeding completed successfully!")


def seed():
    asyncio.run(run_seed())


if __name__ == "__main__":
    seed()
