from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

client = None
db = None

MONGODB_URI = None
DATABASE_NAME = None


async def connect_db():
    global client, db, MONGODB_URI, DATABASE_NAME
    import os
    from dotenv import load_dotenv
    load_dotenv()
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "lab_reports")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    await init_db()
    return db


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db


async def init_db():
    """Create indexes, seed settings and test types."""
    # Indexes
    await db.patients.create_index("phone")
    await db.samples.create_index("sample_id", unique=True)
    await db.tests.create_index("name")
    await db.reports.create_index("report_number", unique=True)
    await db.users.create_index("email", unique=True)

    # Seed settings
    existing = await db.settings.find_one({"_id": "app_settings"})
    if not existing:
        await db.settings.insert_one({
            "_id": "app_settings",
            "lab_name": "LabSync Diagnostics",
            "lab_address": "456 Health Complex",
            "lab_phone": "+91 98765 43210",
            "lab_email": "info@labsync.local",
            "report_prefix": "LR",
            "nabl_number": "MC-12345",
            "currency": "INR",
        })

    # Seed 20 test types
    test_count = await db.tests.count_documents({})
    if test_count == 0:
        now = datetime.now(timezone.utc)
        tests = [
            {
                "name": "Complete Blood Count (CBC)",
                "category": "Hematology",
                "sample_type": "Blood (EDTA)",
                "parameters": [
                    {"name": "Hemoglobin", "unit": "g/dL", "reference_range_male": "13.5-17.5", "reference_range_female": "12.0-15.5"},
                    {"name": "RBC Count", "unit": "million/mcL", "reference_range_male": "4.5-5.5", "reference_range_female": "4.0-5.0"},
                    {"name": "WBC Count", "unit": "cells/mcL", "reference_range_male": "4000-11000", "reference_range_female": "4000-11000"},
                    {"name": "Platelet Count", "unit": "lakh/mcL", "reference_range_male": "1.5-4.0", "reference_range_female": "1.5-4.0"},
                    {"name": "PCV (Hematocrit)", "unit": "%", "reference_range_male": "40-54", "reference_range_female": "36-48"},
                    {"name": "MCV", "unit": "fL", "reference_range_male": "80-100", "reference_range_female": "80-100"},
                    {"name": "MCH", "unit": "pg", "reference_range_male": "27-33", "reference_range_female": "27-33"},
                    {"name": "MCHC", "unit": "g/dL", "reference_range_male": "32-36", "reference_range_female": "32-36"},
                    {"name": "RDW", "unit": "%", "reference_range_male": "11.5-14.5", "reference_range_female": "11.5-14.5"},
                    {"name": "ESR", "unit": "mm/hr", "reference_range_male": "0-15", "reference_range_female": "0-20"},
                ],
                "price": 450,
                "turnaround_hours": 4,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Blood Sugar Fasting",
                "category": "Biochemistry",
                "sample_type": "Blood (Fluoride)",
                "parameters": [
                    {"name": "Blood Sugar Fasting", "unit": "mg/dL", "reference_range_male": "70-100", "reference_range_female": "70-100"},
                ],
                "price": 80,
                "turnaround_hours": 2,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Blood Sugar PP",
                "category": "Biochemistry",
                "sample_type": "Blood (Fluoride)",
                "parameters": [
                    {"name": "Blood Sugar PP", "unit": "mg/dL", "reference_range_male": "70-140", "reference_range_female": "70-140"},
                ],
                "price": 80,
                "turnaround_hours": 2,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "HbA1c",
                "category": "Biochemistry",
                "sample_type": "Blood (EDTA)",
                "parameters": [
                    {"name": "HbA1c", "unit": "%", "reference_range_male": "4.0-5.6", "reference_range_female": "4.0-5.6"},
                ],
                "price": 400,
                "turnaround_hours": 6,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Lipid Profile",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Total Cholesterol", "unit": "mg/dL", "reference_range_male": "<200", "reference_range_female": "<200"},
                    {"name": "Triglycerides", "unit": "mg/dL", "reference_range_male": "<150", "reference_range_female": "<150"},
                    {"name": "HDL Cholesterol", "unit": "mg/dL", "reference_range_male": "40-60", "reference_range_female": "50-60"},
                    {"name": "LDL Cholesterol", "unit": "mg/dL", "reference_range_male": "<100", "reference_range_female": "<100"},
                    {"name": "VLDL Cholesterol", "unit": "mg/dL", "reference_range_male": "<30", "reference_range_female": "<30"},
                    {"name": "Total/HDL Ratio", "unit": "", "reference_range_male": "<4.5", "reference_range_female": "<4.5"},
                ],
                "price": 550,
                "turnaround_hours": 6,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Liver Function Test (LFT)",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Bilirubin Total", "unit": "mg/dL", "reference_range_male": "0.1-1.2", "reference_range_female": "0.1-1.2"},
                    {"name": "Bilirubin Direct", "unit": "mg/dL", "reference_range_male": "0.0-0.3", "reference_range_female": "0.0-0.3"},
                    {"name": "SGOT (AST)", "unit": "U/L", "reference_range_male": "10-40", "reference_range_female": "10-35"},
                    {"name": "SGPT (ALT)", "unit": "U/L", "reference_range_male": "10-40", "reference_range_female": "10-35"},
                    {"name": "Alkaline Phosphatase", "unit": "U/L", "reference_range_male": "44-147", "reference_range_female": "44-147"},
                    {"name": "Total Protein", "unit": "g/dL", "reference_range_male": "6.0-8.3", "reference_range_female": "6.0-8.3"},
                    {"name": "Albumin", "unit": "g/dL", "reference_range_male": "3.5-5.0", "reference_range_female": "3.5-5.0"},
                    {"name": "Globulin", "unit": "g/dL", "reference_range_male": "2.0-3.5", "reference_range_female": "2.0-3.5"},
                ],
                "price": 650,
                "turnaround_hours": 6,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Kidney Function Test (KFT)",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Urea", "unit": "mg/dL", "reference_range_male": "17-43", "reference_range_female": "15-40"},
                    {"name": "Creatinine", "unit": "mg/dL", "reference_range_male": "0.7-1.3", "reference_range_female": "0.6-1.1"},
                    {"name": "Uric Acid", "unit": "mg/dL", "reference_range_male": "3.5-7.2", "reference_range_female": "2.6-6.0"},
                    {"name": "BUN", "unit": "mg/dL", "reference_range_male": "7-20", "reference_range_female": "7-20"},
                    {"name": "eGFR", "unit": "mL/min/1.73m2", "reference_range_male": ">90", "reference_range_female": ">90"},
                ],
                "price": 500,
                "turnaround_hours": 6,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Thyroid Profile",
                "category": "Endocrinology",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "T3 (Triiodothyronine)", "unit": "ng/dL", "reference_range_male": "80-200", "reference_range_female": "80-200"},
                    {"name": "T4 (Thyroxine)", "unit": "mcg/dL", "reference_range_male": "4.5-12.0", "reference_range_female": "4.5-12.0"},
                    {"name": "TSH", "unit": "mIU/L", "reference_range_male": "0.4-4.0", "reference_range_female": "0.4-4.0"},
                ],
                "price": 600,
                "turnaround_hours": 8,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Urine Routine & Microscopy",
                "category": "Clinical Pathology",
                "sample_type": "Urine",
                "parameters": [
                    {"name": "Color", "unit": "", "reference_range_male": "Pale Yellow", "reference_range_female": "Pale Yellow"},
                    {"name": "Appearance", "unit": "", "reference_range_male": "Clear", "reference_range_female": "Clear"},
                    {"name": "pH", "unit": "", "reference_range_male": "4.5-8.0", "reference_range_female": "4.5-8.0"},
                    {"name": "Specific Gravity", "unit": "", "reference_range_male": "1.005-1.030", "reference_range_female": "1.005-1.030"},
                    {"name": "Protein", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                    {"name": "Glucose", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                    {"name": "Ketones", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                    {"name": "Blood", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                    {"name": "WBC", "unit": "/hpf", "reference_range_male": "0-5", "reference_range_female": "0-5"},
                    {"name": "Epithelial Cells", "unit": "/hpf", "reference_range_male": "0-5", "reference_range_female": "0-5"},
                ],
                "price": 200,
                "turnaround_hours": 3,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Vitamin D (25-OH)",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Vitamin D (25-OH)", "unit": "ng/mL", "reference_range_male": "30-100", "reference_range_female": "30-100"},
                ],
                "price": 900,
                "turnaround_hours": 12,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Vitamin B12",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Vitamin B12", "unit": "pg/mL", "reference_range_male": "200-900", "reference_range_female": "200-900"},
                ],
                "price": 800,
                "turnaround_hours": 12,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Iron Studies",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Serum Iron", "unit": "mcg/dL", "reference_range_male": "65-175", "reference_range_female": "50-170"},
                    {"name": "TIBC", "unit": "mcg/dL", "reference_range_male": "250-370", "reference_range_female": "250-370"},
                    {"name": "Transferrin Saturation", "unit": "%", "reference_range_male": "20-50", "reference_range_female": "20-50"},
                    {"name": "Ferritin", "unit": "ng/mL", "reference_range_male": "20-250", "reference_range_female": "10-120"},
                ],
                "price": 750,
                "turnaround_hours": 8,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Blood Group & Rh Typing",
                "category": "Hematology",
                "sample_type": "Blood (EDTA)",
                "parameters": [
                    {"name": "Blood Group (ABO)", "unit": "", "reference_range_male": "A/B/AB/O", "reference_range_female": "A/B/AB/O"},
                    {"name": "Rh Factor", "unit": "", "reference_range_male": "Positive/Negative", "reference_range_female": "Positive/Negative"},
                ],
                "price": 150,
                "turnaround_hours": 2,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Widal Test",
                "category": "Serology",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "S. Typhi O", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                    {"name": "S. Typhi H", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                    {"name": "S. Paratyphi AH", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                    {"name": "S. Paratyphi BH", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                ],
                "price": 300,
                "turnaround_hours": 4,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Dengue NS1 Antigen",
                "category": "Serology",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Dengue NS1 Antigen", "unit": "", "reference_range_male": "Negative", "reference_range_female": "Negative"},
                ],
                "price": 600,
                "turnaround_hours": 4,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "C-Reactive Protein (CRP)",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "CRP (Quantitative)", "unit": "mg/L", "reference_range_male": "<6", "reference_range_female": "<6"},
                ],
                "price": 350,
                "turnaround_hours": 4,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "HIV I & II (Serology)",
                "category": "Serology",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "HIV I & II Antibody", "unit": "", "reference_range_male": "Non-Reactive", "reference_range_female": "Non-Reactive"},
                ],
                "price": 400,
                "turnaround_hours": 6,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "HBsAg (Hepatitis B)",
                "category": "Serology",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "HBsAg", "unit": "", "reference_range_male": "Non-Reactive", "reference_range_female": "Non-Reactive"},
                ],
                "price": 350,
                "turnaround_hours": 6,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Blood Urea Nitrogen",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Blood Urea Nitrogen", "unit": "mg/dL", "reference_range_male": "7-20", "reference_range_female": "7-20"},
                ],
                "price": 120,
                "turnaround_hours": 3,
                "created_at": now, "updated_at": now,
            },
            {
                "name": "Serum Electrolytes",
                "category": "Biochemistry",
                "sample_type": "Blood (Serum)",
                "parameters": [
                    {"name": "Sodium", "unit": "mEq/L", "reference_range_male": "136-145", "reference_range_female": "136-145"},
                    {"name": "Potassium", "unit": "mEq/L", "reference_range_male": "3.5-5.0", "reference_range_female": "3.5-5.0"},
                    {"name": "Chloride", "unit": "mEq/L", "reference_range_male": "98-106", "reference_range_female": "98-106"},
                ],
                "price": 450,
                "turnaround_hours": 4,
                "created_at": now, "updated_at": now,
            },
        ]
        await db.tests.insert_many(tests)
