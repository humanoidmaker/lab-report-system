from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from app.core.database import get_db
from app.utils.auth import get_current_user
import random, string

router = APIRouter(prefix="/api/reports", tags=["reports"])

def s(doc):
    if doc: doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("/")
async def create(data: dict, user=Depends(get_current_user), db=Depends(get_db)):
    now = datetime.now(timezone.utc)
    report_number = f"LR-{now.strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
    report = {
        "report_number": report_number, "sample_id": data["sample_id"],
        "test_id": data["test_id"], "patient_id": data.get("patient_id", ""),
        "results": data.get("results", []), "technician_name": data.get("technician_name", ""),
        "notes": data.get("notes", ""), "status": "pending_verification",
        "verified_by": None, "created_at": now,
    }
    r = await db.reports.insert_one(report)
    return {"success": True, "id": str(r.inserted_id), "report_number": report_number}

@router.get("/")
async def list_reports(status: str = "", patient_id: str = "", db=Depends(get_db), user=Depends(get_current_user)):
    f = {}
    if status: f["status"] = status
    if patient_id: f["patient_id"] = patient_id
    return {"success": True, "reports": [s(d) for d in await db.reports.find(f).sort("created_at", -1).to_list(500)]}

@router.get("/{rid}")
async def get_report(rid: str, db=Depends(get_db), user=Depends(get_current_user)):
    doc = await db.reports.find_one({"_id": ObjectId(rid)})
    if not doc: raise HTTPException(404, "Not found")
    return {"success": True, "report": s(doc)}

@router.put("/{rid}/verify")
async def verify(rid: str, data: dict, user=Depends(get_current_user), db=Depends(get_db)):
    await db.reports.update_one({"_id": ObjectId(rid)}, {"$set": {"status": "verified", "verified_by": data.get("verified_by", user.get("name", ""))}})
    return {"success": True}

@router.get("/{rid}/pdf")
async def report_pdf(rid: str, db=Depends(get_db)):
    report = await db.reports.find_one({"_id": ObjectId(rid)})
    if not report: raise HTTPException(404, "Not found")
    settings_docs = await db.settings.find().to_list(20)
    settings = {d["key"]: d["value"] for d in settings_docs}
    results_html = "".join([
        f"<tr style=\"{'color:red;font-weight:bold' if r.get('is_abnormal') else ''}\"><td>{r['parameter_name']}</td><td>{r['value']}</td><td>{r.get('unit','')}</td><td>{r.get('reference_range','')}</td><td>{'⚠ Abnormal' if r.get('is_abnormal') else 'Normal'}</td></tr>"
        for r in report.get("results", [])
    ])
    html = f"""<html><head><style>body{{font-family:Arial;max-width:700px;margin:0 auto;padding:20px}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#1e3a5f;color:white}}.header{{text-align:center;border-bottom:2px solid #1e3a5f;padding-bottom:10px;margin-bottom:20px}}</style></head>
    <body><div class="header"><h2>{settings.get('lab_name','LabSync')}</h2><p>{settings.get('lab_address','')}</p></div>
    <p><strong>Report #:</strong> {report['report_number']}</p>
    <table><tr><th>Parameter</th><th>Value</th><th>Unit</th><th>Reference Range</th><th>Status</th></tr>{results_html}</table>
    <p style="margin-top:20px"><strong>Technician:</strong> {report.get('technician_name','')}</p>
    <p><strong>Verified by:</strong> {report.get('verified_by','Pending')}</p>
    <p><strong>Status:</strong> {report['status'].replace('_',' ').title()}</p></body></html>"""
    return {"success": True, "html": html}
