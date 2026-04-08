from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from app.core.database import get_db
from app.utils.auth import get_current_user
import random, string

router = APIRouter(prefix="/api/samples", tags=["samples"])

def s(doc):
    if doc: doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("/")
async def create(data: dict, user=Depends(get_current_user), db=Depends(get_db)):
    now = datetime.now(timezone.utc)
    sample_id = f"SMP-{now.strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
    sample = {
        "sample_id": sample_id, "patient_id": data["patient_id"],
        "test_ids": data.get("test_ids", []), "collected_by": data.get("collected_by", ""),
        "priority": data.get("priority", "routine"), "status": "collected", "created_at": now,
    }
    r = await db.samples.insert_one(sample)
    return {"success": True, "id": str(r.inserted_id), "sample_id": sample_id}

@router.get("/")
async def list_samples(status: str = "", date: str = "", db=Depends(get_db), user=Depends(get_current_user)):
    f = {}
    if status: f["status"] = status
    return {"success": True, "samples": [s(d) for d in await db.samples.find(f).sort("created_at", -1).to_list(500)]}

@router.get("/{sid}")
async def get_sample(sid: str, db=Depends(get_db), user=Depends(get_current_user)):
    doc = await db.samples.find_one({"_id": ObjectId(sid)})
    if not doc: raise HTTPException(404, "Not found")
    return {"success": True, "sample": s(doc)}

@router.put("/{sid}/status")
async def update_status(sid: str, data: dict, user=Depends(get_current_user), db=Depends(get_db)):
    await db.samples.update_one({"_id": ObjectId(sid)}, {"$set": {"status": data["status"]}})
    return {"success": True}
