import asyncio
from datetime import datetime
from bson import ObjectId
import pytz
from src.enums.base import Action, Module
from src.core.database import get_collection
from src.utilities.crypto.hash import set_password
from src.configs.env import (
    ADMIN_EMAIL,
    ADMIN_FIRSTNAME,
    ADMIN_LASTNAME,
    ADMIN_PHONENUMBER,
    ADMIN_PASSWORD,
)
from src.enums.base import AdminRole
lagos_tz = pytz.timezone("Africa/Lagos")


# -------------------- HELPERS --------------------

def generate_permissions():
    """Generate all combinations of Module × Action."""
    now = datetime.now(lagos_tz)
    return [
        {
            "action": action.value,
            "resource": module.value,
            "created_at": now,
            "updated_at": None,
        }
        for module in Module
        for action in Action
    ]


# -------------------- SEED FUNCTIONS --------------------

async def seed_permissions():
    """Insert all module permissions if not already present."""
    perm_col = await get_collection("Permissions")
    existing_count = await perm_col.count_documents({})

    if existing_count > 0:
        print("ℹ️ Permissions already exist.")
        return await perm_col.find({}).to_list(length=None)

    permissions = generate_permissions()
    await perm_col.insert_many(permissions)
    print(f"✅ {len(permissions)} permissions created.")

    return await perm_col.find({}).to_list(length=None)


async def seed_permission_groups(permissions):
    """Seed AllAccess, NotePermission, and UserPermission groups."""
    group_col = await get_collection("PermissionGroups")
    now = datetime.now(lagos_tz)

    def filter_perms(modules, actions=None):
        """Filter permission IDs by module and action."""
        return [
            perm["_id"]
            for perm in permissions
            if perm["resource"] in [m.value for m in modules]
            and (actions is None or perm["action"] in [a.value for a in actions])
        ]

    # -------------------- AllAccess --------------------
    all_access = await group_col.find_one({"name": "AllAccess"})
    if not all_access:
        all_access_group = {
            "name": "AllAccess",
            "permissions": [perm["_id"] for perm in permissions],  # all perms
            "created_at": now,
            "updated_at": None,
        }
        await group_col.insert_one(all_access_group)
        print("✅ AllAccess group created.")
    else:
        print("ℹ️ AllAccess group already exists.")

    # -------------------- NotePermission --------------------
    note_existing = await group_col.find_one({"name": "NotePermission"})
    if not note_existing:
        note_group = {
            "name": "NotePermission",
            "permissions": filter_perms([Module.NOTE], list(Action)),
            "created_at": now,
            "updated_at": None,
        }
        await group_col.insert_one(note_group)
        print("✅ NotePermission group created.")
    else:
        print("ℹ️ NotePermission group already exists.")

    # -------------------- UserPermission --------------------
    user_existing = await group_col.find_one({"name": "UserPermission"})
    if not user_existing:
        user_group = {
            "name": "UserPermission",
            "permissions": filter_perms([Module.USER, Module.NOTE], list(Action)),
            "created_at": now,
            "updated_at": None,
        }
        await group_col.insert_one(user_group)
        print("✅ UserPermission group created.")
    else:
        print("ℹ️ UserPermission group already exists.")


async def seed_admin():
    """Seed an admin user with AllAccess permission."""
    admin_col = await get_collection("Admins")
    group_col = await get_collection("PermissionGroups")

    existing_admin = await admin_col.find_one({"email": ADMIN_EMAIL})
    if existing_admin:
        print("ℹ️ Admin already exists.")
        return

    all_access_group = await group_col.find_one({"name": "AllAccess"})
    if not all_access_group:
        raise Exception("❌ AllAccess group not found. Please seed permissions first.")

    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)

    admin_data = {
        "first_name": ADMIN_FIRSTNAME,
        "last_name": ADMIN_LASTNAME,
        "email": ADMIN_EMAIL,
        "phone_number": ADMIN_PHONENUMBER,
        "password": set_password(ADMIN_PASSWORD),
        "role": AdminRole.ADMIN,
        "role": "admin",
        "permission_groups": [all_access_group["_id"]],
        "created_at": now,
        "updated_at": None,
    }

    await admin_col.insert_one(admin_data)
    print("✅ Seeded super admin account.")


# -------------------- RUNNER --------------------

async def run_seed():
    permissions = await seed_permissions()
    await seed_permission_groups(permissions)
    await seed_admin()
    print("🎉 Seeding completed successfully!")


def seed():
    asyncio.run(run_seed())


if __name__ == "__main__":
    seed()
