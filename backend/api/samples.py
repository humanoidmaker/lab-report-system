from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from database import samples_col, patients_col, tests_col, get_next_sequence

router = APIRouter(prefix="/api/samples", tags=["samples"])


def serialize(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
        if "patient_id" in doc and isinstance(doc["patient_id"], ObjectId):
            doc["patient_id"] = str(doc["patient_id"])
        if "test_ids" in doc:
            doc["test_ids"] = [str(t) if isinstance(t, ObjectId) else t for t in doc["test_ids"]]
    return doc


class SampleCreate(BaseModel):
    patient_id: str
    test_ids: List[str]
    collected_by: str
    priority: str = "routine"


@router.get("/")
async def list_samples(
    status: Optional[str] = None,
    date: Optional[str] = None,
    q: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            query["created_at"] = {
                "$gte": d,
                "$lt": datetime(d.year, d.month, d.day, 23, 59, 59),
            }
        except ValueError:
            pass
    if q:
        query["$or"] = [
            {"sample_id": {"$regex": q, "$options": "i"}},
            {"patient_name": {"$regex": q, "$options": "i"}},
        ]
    cursor = samples_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    total = await samples_col.count_documents(query)
    return {"data": results, "total": total}


@router.get("/{sample_id}")
async def get_sample(sample_id: str):
    doc = await samples_col.find_one({"_id": ObjectId(sample_id)})
    if not doc:
        doc = await samples_col.find_one({"sample_id": sample_id})
    if not doc:
        raise HTTPException(404, "Sample not found")
    return serialize(doc)


@router.post("/")
async def create_sample(data: SampleCreate):
    patient = await patients_col.find_one({"_id": ObjectId(data.patient_id)})
    if not patient:
        raise HTTPException(404, "Patient not found")

    test_objects = []
    total_price = 0
    for tid in data.test_ids:
        t = await tests_col.find_one({"_id": ObjectId(tid)})
        if t:
            test_objects.append({"id": str(t["_id"]), "name": t["name"], "price": t.get("price", 0)})
            total_price += t.get("price", 0)

    now = datetime.utcnow()
    seq = await get_next_sequence("sample")
    sample_id_str = f"SMP-{now.strftime('%Y%m%d')}-{seq:04d}"

    doc = {
        "sample_id": sample_id_str,
        "patient_id": ObjectId(data.patient_id),
        "patient_name": patient["name"],
        "patient_phone": patient.get("phone", ""),
        "test_ids": [ObjectId(t) for t in data.test_ids],
        "tests": test_objects,
        "total_price": total_price,
        "collected_by": data.collected_by,
        "priority": data.priority,
        "status": "collected",
        "created_at": now,
        "updated_at": now,
    }
    result = await samples_col.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    doc["patient_id"] = str(doc["patient_id"])
    doc["test_ids"] = [str(t) for t in doc["test_ids"]]
    return doc


@router.put("/{sample_id}/status")
async def update_sample_status(sample_id: str, status: str = Query(...)):
    valid_transitions = {
        "collected": "processing",
        "processing": "completed",
    }
    doc = await samples_col.find_one({"_id": ObjectId(sample_id)})
    if not doc:
        raise HTTPException(404, "Sample not found")
    current = doc["status"]
    if valid_transitions.get(current) != status:
        raise HTTPException(400, f"Cannot transition from {current} to {status}")
    await samples_col.update_one(
        {"_id": ObjectId(sample_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    doc = await samples_col.find_one({"_id": ObjectId(sample_id)})
    return serialize(doc)
