from fastapi import APIRouter, Depends
from bson import ObjectId
from app.core.database import get_db
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/tests", tags=["tests"])

def s(doc):
    if doc: doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/")
async def list_tests(category: str = "", db=Depends(get_db)):
    f = {}
    if category: f["category"] = category
    return {"success": True, "tests": [s(d) for d in await db.tests.find(f).sort("name", 1).to_list(100)]}

@router.get("/categories")
async def categories(db=Depends(get_db)):
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
    return {"success": True, "categories": [{"name": r["_id"], "count": r["count"]} for r in await db.tests.aggregate(pipeline).to_list(50)]}

@router.post("/")
async def create(data: dict, user=Depends(get_current_user), db=Depends(get_db)):
    r = await db.tests.insert_one(data)
    return {"success": True, "id": str(r.inserted_id)}

@router.put("/{tid}")
async def update(tid: str, data: dict, user=Depends(get_current_user), db=Depends(get_db)):
    data.pop("id", None); data.pop("_id", None)
    await db.tests.update_one({"_id": ObjectId(tid)}, {"$set": data})
    return {"success": True}
