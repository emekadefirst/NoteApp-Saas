import asyncio
from datetime import datetime
from bson import ObjectId
import pytz
from src.enums.base import Action, Module
from src.core.database import get_collection

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


async def seed_permission_group(permissions):
    """Create a single permission group containing all permissions."""
    group_col = await get_collection("PermissionGroups")

    existing = await group_col.find_one({"name": "FullAccessGroup"})
    if existing:
        print("ℹ️ FullAccessGroup already exists.")
        return existing

    group_data = {
        "name": "FullAccessGroup",
        "permissions": [perm["_id"] for perm in permissions],
        "created_at": datetime.now(lagos_tz),
        "updated_at": None,
    }

    result = await group_col.insert_one(group_data)
    print("✅ FullAccessGroup created successfully.")
    return await group_col.find_one({"_id": result.inserted_id})


# -------------------- RUNNER --------------------

async def run_seed():
    permissions = await seed_permissions()
    await seed_permission_group(permissions)
    print("🎉 Permission seeding completed successfully!")


def seed():
    asyncio.run(run_seed())


if __name__ == "__main__":
    seed()
