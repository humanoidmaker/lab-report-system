from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from database import settings_col
from auth import get_current_user

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    lab_name: Optional[str] = None
    lab_address: Optional[str] = None
    lab_phone: Optional[str] = None
    lab_email: Optional[str] = None
    report_prefix: Optional[str] = None
    nabl_number: Optional[str] = None
    currency: Optional[str] = None


@router.get("/")
async def get_settings():
    settings = await settings_col.find_one({"_id": "app_settings"})
    if settings:
        settings["id"] = str(settings.pop("_id"))
    return settings or {}


@router.put("/")
async def update_settings(data: SettingsUpdate, user=Depends(get_current_user)):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if update_data:
        await settings_col.update_one(
            {"_id": "app_settings"},
            {"$set": update_data},
            upsert=True,
        )
    settings = await settings_col.find_one({"_id": "app_settings"})
    if settings:
        settings["id"] = str(settings.pop("_id"))
    return settings
