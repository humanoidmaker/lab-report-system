from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from database import tests_col

router = APIRouter(prefix="/api/tests", tags=["tests"])


def serialize(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


class TestParameter(BaseModel):
    name: str
    unit: str
    reference_range_male: str
    reference_range_female: str


class TestCreate(BaseModel):
    name: str
    category: str
    sample_type: str
    description: Optional[str] = ""
    parameters: List[TestParameter] = []
    price: float
    turnaround_hours: int = 24


class TestUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sample_type: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[List[TestParameter]] = None
    price: Optional[float] = None
    turnaround_hours: Optional[int] = None


@router.get("/")
async def list_tests(skip: int = 0, limit: int = 100):
    cursor = tests_col.find().sort("name", 1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    total = await tests_col.count_documents({})
    return {"data": results, "total": total}


@router.get("/categories")
async def get_categories():
    categories = await tests_col.distinct("category")
    return {"data": categories}


@router.get("/by-category/{category}")
async def get_by_category(category: str):
    cursor = tests_col.find({"category": category}).sort("name", 1)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    return {"data": results}


@router.get("/{test_id}")
async def get_test(test_id: str):
    doc = await tests_col.find_one({"_id": ObjectId(test_id)})
    if not doc:
        raise HTTPException(404, "Test not found")
    return serialize(doc)


@router.post("/")
async def create_test(data: TestCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    result = await tests_col.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc


@router.put("/{test_id}")
async def update_test(test_id: str, data: TestUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    result = await tests_col.update_one(
        {"_id": ObjectId(test_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Test not found")
    doc = await tests_col.find_one({"_id": ObjectId(test_id)})
    return serialize(doc)


@router.delete("/{test_id}")
async def delete_test(test_id: str):
    result = await tests_col.delete_one({"_id": ObjectId(test_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Test not found")
    return {"message": "Test deleted"}
