from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, DATABASE_NAME

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

patients_col = db["patients"]
tests_col = db["tests"]
samples_col = db["samples"]
reports_col = db["reports"]
users_col = db["users"]
settings_col = db["settings"]
counters_col = db["counters"]


async def get_next_sequence(name: str) -> int:
    result = await counters_col.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return result["seq"]


async def init_db():
    await patients_col.create_index("phone")
    await samples_col.create_index("sample_id", unique=True)
    await tests_col.create_index("name")
    await reports_col.create_index("report_number", unique=True)
    await users_col.create_index("email", unique=True)

    existing = await settings_col.find_one({"_id": "app_settings"})
    if not existing:
        await settings_col.insert_one({
            "_id": "app_settings",
            "lab_name": "LabSync Diagnostics",
            "lab_address": "123 Health Street, Medical Complex, Mumbai 400001",
            "lab_phone": "+91 22 1234 5678",
            "lab_email": "info@labsync.local",
            "report_prefix": "LR",
            "nabl_number": "MC-12345",
            "currency": "INR",
        })
