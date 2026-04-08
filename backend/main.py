from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from api.auth_routes import router as auth_router
from api.settings_routes import router as settings_router
from api.patients import router as patients_router
from api.tests import router as tests_router
from api.samples import router as samples_router
from api.reports import router as reports_router
from config import PORT

app = FastAPI(title="LabSync API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(settings_router)
app.include_router(patients_router)
app.include_router(tests_router)
app.include_router(samples_router)
app.include_router(reports_router)


@app.on_event("startup")
async def startup():
    await init_db()
    from api.auth_routes import seed_admin
    await seed_admin()


@app.get("/api/stats")
async def global_stats():
    from database import patients_col, samples_col, reports_col, tests_col
    from datetime import datetime, timedelta

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    return {
        "total_patients": await patients_col.count_documents({}),
        "total_tests": await tests_col.count_documents({}),
        "total_samples": await samples_col.count_documents({}),
        "total_reports": await reports_col.count_documents({}),
        "today_samples": await samples_col.count_documents({"created_at": {"$gte": today, "$lt": tomorrow}}),
        "pending_reports": await reports_col.count_documents({"status": "pending_verification"}),
        "verified_today": await reports_col.count_documents({"status": "verified", "verified_at": {"$gte": today, "$lt": tomorrow}}),
    }


@app.get("/")
async def root():
    return {"app": "LabSync", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
