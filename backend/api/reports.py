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

    # Revenue stats
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue_pipeline = [
        {"$match": {"created_at": {"$gte": month_start}}},
        {"$lookup": {"from": "samples", "localField": "sample_id", "foreignField": "_id", "as": "sample_info"}},
        {"$unwind": {"path": "$sample_info", "preserveNullAndEmptyArrays": True}},
        {"$group": {"_id": None, "total": {"$sum": "$sample_info.total_price"}}},
    ]
    rev_result = await reports_col.aggregate(revenue_pipeline).to_list(1)
    monthly_revenue = rev_result[0]["total"] if rev_result else 0

    return {
        "today_samples": today_samples,
        "pending_results": pending_results,
        "verified_today": verified_today,
        "total_patients": total_patients,
        "monthly_revenue": round(monthly_revenue, 2),
        "pipeline": {"collected": collected, "processing": processing, "completed": completed},
    }


@router.get("/")
async def list_reports(
    status: Optional[str] = None,
    patient_id: Optional[str] = None,
    date: Optional[str] = None,
    q: Optional[str] = None,
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
    if q:
        query["$or"] = [
            {"report_number": {"$regex": q, "$options": "i"}},
            {"patient_name": {"$regex": q, "$options": "i"}},
            {"test_name": {"$regex": q, "$options": "i"}},
        ]

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
        "results": [r.model_dump() for r in data.results],
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
            "verified_by": pathologist_name,
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
        flag = "HIGH" if r.get("is_abnormal") else "Normal"
        flag_color = "#dc2626" if r.get("is_abnormal") else "#16a34a"
        results_rows += f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">{r['parameter_name']}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;{color}">{r['value']}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">{r['unit']}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">{r['reference_range']}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;color:{flag_color};font-weight:600;">{flag}</td>
        </tr>"""

    verified_section = ""
    if doc.get("status") == "verified":
        verified_section = f"""
        <div style="margin-top:40px;display:flex;justify-content:space-between;padding:0 40px;">
            <div style="text-align:center;">
                <div style="border-top:2px solid #333;padding-top:8px;width:220px;">
                    <strong>{doc.get('technician_name', 'N/A')}</strong><br>
                    <small style="color:#666;">Medical Lab Technician</small>
                </div>
            </div>
            <div style="text-align:center;">
                <div style="border-top:2px solid #333;padding-top:8px;width:220px;">
                    <strong>{doc.get('pathologist_name', 'N/A')}</strong><br>
                    <small style="color:#666;">Consultant Pathologist</small>
                </div>
            </div>
        </div>
        """

    status_badge = ""
    if doc["status"] == "verified":
        status_badge = '<span style="background:#16a34a;color:white;padding:4px 12px;border-radius:12px;font-size:12px;">VERIFIED</span>'
    else:
        status_badge = '<span style="background:#f59e0b;color:white;padding:4px 12px;border-radius:12px;font-size:12px;">PENDING VERIFICATION</span>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Lab Report - {doc['report_number']}</title>
    <style>
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body style="font-family:'Segoe UI',Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;color:#1f2937;">
    <!-- Lab Header -->
    <div style="text-align:center;border-bottom:3px solid #1e3a5f;padding-bottom:15px;margin-bottom:20px;">
        <h1 style="color:#1e3a5f;margin:0 0 5px 0;font-size:28px;letter-spacing:1px;">{lab_name}</h1>
        <p style="margin:3px 0;color:#4b5563;font-size:14px;">{lab_address}</p>
        <p style="margin:3px 0;color:#4b5563;font-size:14px;">Phone: {lab_phone} | NABL Accredited: {nabl}</p>
    </div>

    <h2 style="text-align:center;color:#1e3a5f;margin:10px 0;font-size:18px;text-transform:uppercase;letter-spacing:2px;">
        Laboratory Test Report
    </h2>

    <!-- Patient Info + Report Info -->
    <div style="display:flex;justify-content:space-between;margin-bottom:20px;background:#f8fafc;padding:15px;border-radius:8px;border:1px solid #e2e8f0;">
        <div style="flex:1;">
            <p style="margin:4px 0;"><strong>Patient Name:</strong> {doc.get('patient_name','N/A')}</p>
            <p style="margin:4px 0;"><strong>Age / Gender:</strong> {doc.get('patient_age','')}/{doc.get('patient_gender','')}</p>
            <p style="margin:4px 0;"><strong>Ref. Doctor:</strong> {doc.get('doctor_name','N/A')}</p>
        </div>
        <div style="flex:1;text-align:right;">
            <p style="margin:4px 0;"><strong>Report #:</strong> {doc['report_number']}</p>
            <p style="margin:4px 0;"><strong>Sample ID:</strong> {doc.get('sample_code','')}</p>
            <p style="margin:4px 0;"><strong>Date:</strong> {doc['created_at'].strftime('%d-%b-%Y %I:%M %p')}</p>
            <p style="margin:4px 0;">{status_badge}</p>
        </div>
    </div>

    <!-- Test Name Banner -->
    <div style="background:#1e3a5f;color:white;padding:10px 16px;border-radius:6px 6px 0 0;margin-bottom:0;">
        <h3 style="margin:0;font-size:16px;">{doc.get('test_name','')} <span style="font-weight:normal;font-size:13px;opacity:0.8;">({doc.get('test_category','')})</span></h3>
    </div>

    <!-- Results Table -->
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;border:1px solid #e5e7eb;">
        <thead>
            <tr style="background:#f1f5f9;">
                <th style="padding:10px 12px;text-align:left;font-size:13px;color:#475569;border-bottom:2px solid #cbd5e1;">Parameter</th>
                <th style="padding:10px 12px;text-align:left;font-size:13px;color:#475569;border-bottom:2px solid #cbd5e1;">Value</th>
                <th style="padding:10px 12px;text-align:left;font-size:13px;color:#475569;border-bottom:2px solid #cbd5e1;">Unit</th>
                <th style="padding:10px 12px;text-align:left;font-size:13px;color:#475569;border-bottom:2px solid #cbd5e1;">Reference Range</th>
                <th style="padding:10px 12px;text-align:left;font-size:13px;color:#475569;border-bottom:2px solid #cbd5e1;">Status</th>
            </tr>
        </thead>
        <tbody>{results_rows}</tbody>
    </table>

    {"<div style='margin-bottom:20px;padding:10px;background:#fffbeb;border:1px solid #fde68a;border-radius:6px;'><strong>Notes:</strong> " + doc['notes'] + "</div>" if doc.get('notes') else ""}

    {verified_section}

    <!-- Footer -->
    <div style="margin-top:40px;text-align:center;border-top:2px solid #e5e7eb;padding-top:12px;color:#9ca3af;font-size:11px;">
        <p style="margin:2px 0;">*** End of Report ***</p>
        <p style="margin:2px 0;">This is a computer-generated report. | Generated by {lab_name}</p>
        <p style="margin:2px 0;">Please correlate clinically. Consult your doctor for interpretation.</p>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)
