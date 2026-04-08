from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, patients, tests, samples, reports, settings as settings_api

@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield

app = FastAPI(title="LabSync API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(tests.router)
app.include_router(samples.router)
app.include_router(reports.router)
app.include_router(settings_api.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "LabSync"}

@app.get("/api/stats")
async def stats():
    from app.core.database import get_db as gdb
    from datetime import datetime, timezone
    db = await gdb()
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tp = await db.patients.count_documents({})
    ts = await db.samples.count_documents({"created_at": {"$gte": start}})
    pending = await db.reports.count_documents({"status": "pending_verification"})
    verified = await db.reports.count_documents({"status": "verified"})
    return {"stats": {"total_patients": tp, "today_samples": ts, "pending_reports": pending, "verified_reports": verified}}
