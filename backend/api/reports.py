from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timedelta
from database import reports_col, samples_col, tests_col, patients_col, settings_col, get_next_sequence

router = APIRouter(prefix="/api/reports", tags=["reports"])


def serialize(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
        for key in ["sample_id", "test_id", "patient_id"]:
            if key in doc and isinstance(doc[key], ObjectId):
                doc[key] = str(doc[key])
    return doc


class ResultEntry(BaseModel):
    parameter_name: str
    value: str
    unit: str
    reference_range: str
    is_abnormal: bool = False


class ReportCreate(BaseModel):
    sample_id: str
    test_id: str
    results: List[ResultEntry]
    technician_name: str
    notes: Optional[str] = ""


@router.get("/stats")
async def report_stats():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    today_samples = await samples_col.count_documents({
        "created_at": {"$gte": today, "$lt": tomorrow}
    })
    pending_results = await reports_col.count_documents({"status": "pending_verification"})
    verified_today = await reports_col.count_documents({
        "status": "verified",
        "verified_at": {"$gte": today, "$lt": tomorrow}
    })
    total_patients = await patients_col.count_documents({})

    collected = await samples_col.count_documents({"status": "collected"})
    processing = await samples_col.count_documents({"status": "processing"})
    completed = await samples_col.count_documents({"status": "completed"})

    return {
        "today_samples": today_samples,
        "pending_results": pending_results,
        "verified_today": verified_today,
        "total_patients": total_patients,
        "pipeline": {"collected": collected, "processing": processing, "completed": completed},
    }


@router.get("/")
async def list_reports(
    status: Optional[str] = None,
    patient_id: Optional[str] = None,
    date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = {}
    if status:
        query["status"] = status
    if patient_id:
        query["patient_id"] = ObjectId(patient_id)
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            query["created_at"] = {"$gte": d, "$lt": datetime(d.year, d.month, d.day, 23, 59, 59)}
        except ValueError:
            pass

    cursor = reports_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    total = await reports_col.count_documents(query)
    return {"data": results, "total": total}


@router.get("/{report_id}")
async def get_report(report_id: str):
    doc = await reports_col.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(404, "Report not found")
    return serialize(doc)


@router.post("/")
async def create_report(data: ReportCreate):
    sample = await samples_col.find_one({"_id": ObjectId(data.sample_id)})
    if not sample:
        raise HTTPException(404, "Sample not found")

    test = await tests_col.find_one({"_id": ObjectId(data.test_id)})
    if not test:
        raise HTTPException(404, "Test not found")

    patient = await patients_col.find_one({"_id": sample["patient_id"]})

    settings = await settings_col.find_one({"_id": "app_settings"})
    prefix = settings.get("report_prefix", "LR") if settings else "LR"

    now = datetime.utcnow()
    seq = await get_next_sequence("report")
    report_number = f"{prefix}-{now.strftime('%Y%m%d')}-{seq:04d}"

    doc = {
        "report_number": report_number,
        "sample_id": ObjectId(data.sample_id),
        "sample_code": sample["sample_id"],
        "test_id": ObjectId(data.test_id),
        "test_name": test["name"],
        "test_category": test.get("category", ""),
        "patient_id": sample["patient_id"],
        "patient_name": patient["name"] if patient else "",
        "patient_age": patient.get("age", 0) if patient else 0,
        "patient_gender": patient.get("gender", "") if patient else "",
        "doctor_name": patient.get("doctor_name", "") if patient else "",
        "results": [r.dict() for r in data.results],
        "technician_name": data.technician_name,
        "notes": data.notes,
        "status": "pending_verification",
        "created_at": now,
        "updated_at": now,
    }
    result = await reports_col.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    doc["sample_id"] = str(doc["sample_id"])
    doc["test_id"] = str(doc["test_id"])
    doc["patient_id"] = str(doc["patient_id"])
    return doc


@router.put("/{report_id}/verify")
async def verify_report(report_id: str, pathologist_name: str = Query("Pathologist")):
    doc = await reports_col.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(404, "Report not found")
    if doc["status"] != "pending_verification":
        raise HTTPException(400, "Report already verified")

    now = datetime.utcnow()
    await reports_col.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {
            "status": "verified",
            "pathologist_name": pathologist_name,
            "verified_at": now,
            "updated_at": now,
        }}
    )
    doc = await reports_col.find_one({"_id": ObjectId(report_id)})
    return serialize(doc)


@router.get("/{report_id}/pdf")
async def report_pdf(report_id: str):
    doc = await reports_col.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(404, "Report not found")

    settings = await settings_col.find_one({"_id": "app_settings"})
    lab_name = settings.get("lab_name", "Lab") if settings else "Lab"
    lab_address = settings.get("lab_address", "") if settings else ""
    lab_phone = settings.get("lab_phone", "") if settings else ""
    nabl = settings.get("nabl_number", "") if settings else ""

    results_rows = ""
    for r in doc.get("results", []):
        color = "color: #dc2626; font-weight: bold;" if r.get("is_abnormal") else ""
        flag = "H" if r.get("is_abnormal") else ""
        results_rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ddd;">{r['parameter_name']}</td>
            <td style="padding:8px;border:1px solid #ddd;{color}">{r['value']}</td>
            <td style="padding:8px;border:1px solid #ddd;">{r['unit']}</td>
            <td style="padding:8px;border:1px solid #ddd;">{r['reference_range']}</td>
            <td style="padding:8px;border:1px solid #ddd;{color}">{flag}</td>
        </tr>"""

    verified_section = ""
    if doc.get("status") == "verified":
        verified_section = f"""
        <div style="margin-top:30px;display:flex;justify-content:space-between;">
            <div style="text-align:center;">
                <div style="border-top:1px solid #333;padding-top:5px;width:200px;">
                    {doc.get('technician_name', 'N/A')}<br><small>Medical Technician</small>
                </div>
            </div>
            <div style="text-align:center;">
                <div style="border-top:1px solid #333;padding-top:5px;width:200px;">
                    {doc.get('pathologist_name', 'N/A')}<br><small>Pathologist</small>
                </div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Report {doc['report_number']}</title></head>
<body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;">
    <div style="text-align:center;border-bottom:3px solid #1e3a5f;padding-bottom:15px;margin-bottom:20px;">
        <h1 style="color:#1e3a5f;margin:0;">{lab_name}</h1>
        <p style="margin:5px 0;color:#666;">{lab_address}</p>
        <p style="margin:5px 0;color:#666;">Phone: {lab_phone} | NABL: {nabl}</p>
    </div>

    <div style="display:flex;justify-content:space-between;margin-bottom:20px;">
        <div>
            <strong>Patient:</strong> {doc.get('patient_name','N/A')}<br>
            <strong>Age/Gender:</strong> {doc.get('patient_age','')}/{doc.get('patient_gender','')}<br>
            <strong>Ref. Doctor:</strong> {doc.get('doctor_name','N/A')}
        </div>
        <div style="text-align:right;">
            <strong>Report #:</strong> {doc['report_number']}<br>
            <strong>Sample ID:</strong> {doc.get('sample_code','')}<br>
            <strong>Date:</strong> {doc['created_at'].strftime('%d-%m-%Y %H:%M')}<br>
            <strong>Status:</strong> <span style="color:{'green' if doc['status']=='verified' else 'orange'};">{doc['status'].upper()}</span>
        </div>
    </div>

    <h3 style="background:#1e3a5f;color:white;padding:8px 12px;margin-bottom:0;">
        {doc.get('test_name','')} ({doc.get('test_category','')})
    </h3>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <thead>
            <tr style="background:#f3f4f6;">
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Parameter</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Value</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Unit</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Reference Range</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Flag</th>
            </tr>
        </thead>
        <tbody>{results_rows}</tbody>
    </table>

    {"<div style='margin-bottom:20px;'><strong>Notes:</strong> " + doc['notes'] + "</div>" if doc.get('notes') else ""}

    {verified_section}

    <div style="margin-top:40px;text-align:center;border-top:1px solid #ddd;padding-top:10px;color:#999;font-size:12px;">
        <p>*** End of Report *** | QR Code: [PLACEHOLDER] | Generated by LabSync</p>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)
