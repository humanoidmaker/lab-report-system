from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from database import patients_col

router = APIRouter(prefix="/api/patients", tags=["patients"])


def serialize(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    email: Optional[str] = ""
    doctor_name: Optional[str] = ""
    doctor_phone: Optional[str] = ""
    address: Optional[str] = ""


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    address: Optional[str] = None


@router.get("/")
async def list_patients(skip: int = 0, limit: int = 100):
    cursor = patients_col.find().sort("created_at", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    total = await patients_col.count_documents({})
    return {"data": results, "total": total}


@router.get("/search")
async def search_patients(q: str = Query("")):
    if not q:
        return {"data": []}
    query = {"$or": [
        {"name": {"$regex": q, "$options": "i"}},
        {"phone": {"$regex": q, "$options": "i"}},
        {"email": {"$regex": q, "$options": "i"}},
    ]}
    cursor = patients_col.find(query).limit(20)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    return {"data": results}


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    doc = await patients_col.find_one({"_id": ObjectId(patient_id)})
    if not doc:
        raise HTTPException(404, "Patient not found")
    return serialize(doc)


@router.post("/")
async def create_patient(data: PatientCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    result = await patients_col.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc


@router.put("/{patient_id}")
async def update_patient(patient_id: str, data: PatientUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    result = await patients_col.update_one(
        {"_id": ObjectId(patient_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Patient not found")
    doc = await patients_col.find_one({"_id": ObjectId(patient_id)})
    return serialize(doc)


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    result = await patients_col.delete_one({"_id": ObjectId(patient_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Patient not found")
    return {"message": "Patient deleted"}
