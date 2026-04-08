"""Seed sample data: 15 patients, 20 samples, 20 reports with realistic values."""
import asyncio
import random
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "lab_reports")

PATIENTS = [
    {"name": "Rajesh Kumar", "age": 45, "gender": "Male", "phone": "9876543210", "email": "rajesh.kumar@email.com", "doctor_name": "Dr. Amit Verma", "doctor_phone": "9812345678", "address": "12 MG Road, Mumbai"},
    {"name": "Priya Sharma", "age": 32, "gender": "Female", "phone": "9876543211", "email": "priya.sharma@email.com", "doctor_name": "Dr. Sunita Rao", "doctor_phone": "9812345679", "address": "45 Park Street, Delhi"},
    {"name": "Amit Patel", "age": 58, "gender": "Male", "phone": "9876543212", "email": "amit.patel@email.com", "doctor_name": "Dr. R.K. Gupta", "doctor_phone": "9812345680", "address": "78 Nehru Nagar, Ahmedabad"},
    {"name": "Sunita Devi", "age": 65, "gender": "Female", "phone": "9876543213", "email": "sunita.devi@email.com", "doctor_name": "Dr. Vivek Sharma", "doctor_phone": "9812345681", "address": "23 Civil Lines, Jaipur"},
    {"name": "Vikram Singh", "age": 28, "gender": "Male", "phone": "9876543214", "email": "vikram.singh@email.com", "doctor_name": "Dr. Priya Mehta", "doctor_phone": "9812345682", "address": "56 Lajpat Nagar, Delhi"},
    {"name": "Neha Gupta", "age": 35, "gender": "Female", "phone": "9876543215", "email": "neha.gupta@email.com", "doctor_name": "Dr. Sanjay Kapoor", "doctor_phone": "9812345683", "address": "89 Banjara Hills, Hyderabad"},
    {"name": "Arjun Reddy", "age": 42, "gender": "Male", "phone": "9876543216", "email": "arjun.reddy@email.com", "doctor_name": "Dr. Meena Iyer", "doctor_phone": "9812345684", "address": "34 Jubilee Hills, Hyderabad"},
    {"name": "Kavitha Iyer", "age": 50, "gender": "Female", "phone": "9876543217", "email": "kavitha.iyer@email.com", "doctor_name": "Dr. Ramesh Nair", "doctor_phone": "9812345685", "address": "67 Koramangala, Bangalore"},
    {"name": "Suresh Nair", "age": 70, "gender": "Male", "phone": "9876543218", "email": "suresh.nair@email.com", "doctor_name": "Dr. Anjali Das", "doctor_phone": "9812345686", "address": "12 Marine Drive, Kochi"},
    {"name": "Anita Deshmukh", "age": 8, "gender": "Female", "phone": "9876543219", "email": "parent.deshmukh@email.com", "doctor_name": "Dr. Milind Joshi", "doctor_phone": "9812345687", "address": "45 Deccan, Pune"},
    {"name": "Manoj Tiwari", "age": 55, "gender": "Male", "phone": "9876543220", "email": "manoj.tiwari@email.com", "doctor_name": "Dr. Geeta Pandey", "doctor_phone": "9812345688", "address": "78 Gomti Nagar, Lucknow"},
    {"name": "Deepa Menon", "age": 38, "gender": "Female", "phone": "9876543221", "email": "deepa.menon@email.com", "doctor_name": "Dr. Vijay Kumar", "doctor_phone": "9812345689", "address": "23 Thiruvananthapuram"},
    {"name": "Sanjay Mishra", "age": 48, "gender": "Male", "phone": "9876543222", "email": "sanjay.mishra@email.com", "doctor_name": "Dr. Rekha Singh", "doctor_phone": "9812345690", "address": "56 Varanasi, UP"},
    {"name": "Pooja Verma", "age": 25, "gender": "Female", "phone": "9876543223", "email": "pooja.verma@email.com", "doctor_name": "Dr. Ashok Sharma", "doctor_phone": "9812345691", "address": "89 Sector 17, Chandigarh"},
    {"name": "Rohit Jain", "age": 12, "gender": "Male", "phone": "9876543224", "email": "parent.jain@email.com", "doctor_name": "Dr. Neeta Bhatia", "doctor_phone": "9812345692", "address": "34 Lal Bagh, Indore"},
]

# Realistic result values generators keyed by test name
RESULT_GENERATORS = {
    "Complete Blood Count (CBC)": lambda gender, abnormal: [
        {"parameter_name": "Hemoglobin", "value": str(round(random.uniform(8.5, 11.0) if abnormal else random.uniform(13.5, 16.0) if gender == "Male" else random.uniform(12.0, 14.5), 1)), "unit": "g/dL", "reference_range": "13.5-17.5" if gender == "Male" else "12.0-15.5", "is_abnormal": abnormal},
        {"parameter_name": "RBC Count", "value": str(round(random.uniform(3.2, 3.9) if abnormal else random.uniform(4.5, 5.5) if gender == "Male" else random.uniform(4.0, 5.0), 2)), "unit": "million/mcL", "reference_range": "4.5-5.5" if gender == "Male" else "4.0-5.0", "is_abnormal": abnormal},
        {"parameter_name": "WBC Count", "value": str(random.randint(13000, 18000) if abnormal else random.randint(5000, 9000)), "unit": "cells/mcL", "reference_range": "4000-11000", "is_abnormal": abnormal},
        {"parameter_name": "Platelet Count", "value": str(round(random.uniform(1.5, 3.5), 1)), "unit": "lakh/mcL", "reference_range": "1.5-4.0", "is_abnormal": False},
        {"parameter_name": "PCV (Hematocrit)", "value": str(round(random.uniform(42, 50) if gender == "Male" else random.uniform(37, 45), 1)), "unit": "%", "reference_range": "40-54" if gender == "Male" else "36-48", "is_abnormal": False},
        {"parameter_name": "MCV", "value": str(round(random.uniform(82, 96), 1)), "unit": "fL", "reference_range": "80-100", "is_abnormal": False},
        {"parameter_name": "MCH", "value": str(round(random.uniform(28, 32), 1)), "unit": "pg", "reference_range": "27-33", "is_abnormal": False},
        {"parameter_name": "MCHC", "value": str(round(random.uniform(32.5, 35.5), 1)), "unit": "g/dL", "reference_range": "32-36", "is_abnormal": False},
        {"parameter_name": "RDW", "value": str(round(random.uniform(12.0, 14.0), 1)), "unit": "%", "reference_range": "11.5-14.5", "is_abnormal": False},
        {"parameter_name": "ESR", "value": str(random.randint(35, 60) if abnormal else random.randint(3, 12)), "unit": "mm/hr", "reference_range": "0-15" if gender == "Male" else "0-20", "is_abnormal": abnormal},
    ],
    "Blood Sugar Fasting": lambda gender, abnormal: [
        {"parameter_name": "Blood Sugar Fasting", "value": str(random.randint(140, 250) if abnormal else random.randint(75, 95)), "unit": "mg/dL", "reference_range": "70-100", "is_abnormal": abnormal},
    ],
    "Blood Sugar PP": lambda gender, abnormal: [
        {"parameter_name": "Blood Sugar PP", "value": str(random.randint(180, 320) if abnormal else random.randint(90, 130)), "unit": "mg/dL", "reference_range": "70-140", "is_abnormal": abnormal},
    ],
    "HbA1c": lambda gender, abnormal: [
        {"parameter_name": "HbA1c", "value": str(round(random.uniform(7.5, 11.0) if abnormal else random.uniform(4.2, 5.4), 1)), "unit": "%", "reference_range": "4.0-5.6", "is_abnormal": abnormal},
    ],
    "Lipid Profile": lambda gender, abnormal: [
        {"parameter_name": "Total Cholesterol", "value": str(random.randint(240, 310) if abnormal else random.randint(150, 190)), "unit": "mg/dL", "reference_range": "<200", "is_abnormal": abnormal},
        {"parameter_name": "Triglycerides", "value": str(random.randint(200, 350) if abnormal else random.randint(80, 140)), "unit": "mg/dL", "reference_range": "<150", "is_abnormal": abnormal},
        {"parameter_name": "HDL Cholesterol", "value": str(random.randint(25, 35) if abnormal else random.randint(45, 58)), "unit": "mg/dL", "reference_range": "40-60" if gender == "Male" else "50-60", "is_abnormal": abnormal},
        {"parameter_name": "LDL Cholesterol", "value": str(random.randint(130, 190) if abnormal else random.randint(60, 95)), "unit": "mg/dL", "reference_range": "<100", "is_abnormal": abnormal},
        {"parameter_name": "VLDL Cholesterol", "value": str(random.randint(35, 60) if abnormal else random.randint(10, 28)), "unit": "mg/dL", "reference_range": "<30", "is_abnormal": abnormal},
        {"parameter_name": "Total/HDL Ratio", "value": str(round(random.uniform(5.5, 8.0) if abnormal else random.uniform(3.0, 4.2), 1)), "unit": "", "reference_range": "<4.5", "is_abnormal": abnormal},
    ],
    "Liver Function Test (LFT)": lambda gender, abnormal: [
        {"parameter_name": "Bilirubin Total", "value": str(round(random.uniform(2.0, 4.5) if abnormal else random.uniform(0.3, 1.0), 1)), "unit": "mg/dL", "reference_range": "0.1-1.2", "is_abnormal": abnormal},
        {"parameter_name": "Bilirubin Direct", "value": str(round(random.uniform(0.5, 1.5) if abnormal else random.uniform(0.05, 0.25), 2)), "unit": "mg/dL", "reference_range": "0.0-0.3", "is_abnormal": abnormal},
        {"parameter_name": "SGOT (AST)", "value": str(random.randint(65, 150) if abnormal else random.randint(15, 35)), "unit": "U/L", "reference_range": "10-40" if gender == "Male" else "10-35", "is_abnormal": abnormal},
        {"parameter_name": "SGPT (ALT)", "value": str(random.randint(70, 180) if abnormal else random.randint(12, 35)), "unit": "U/L", "reference_range": "10-40" if gender == "Male" else "10-35", "is_abnormal": abnormal},
        {"parameter_name": "Alkaline Phosphatase", "value": str(random.randint(55, 130)), "unit": "U/L", "reference_range": "44-147", "is_abnormal": False},
        {"parameter_name": "Total Protein", "value": str(round(random.uniform(6.5, 7.8), 1)), "unit": "g/dL", "reference_range": "6.0-8.3", "is_abnormal": False},
        {"parameter_name": "Albumin", "value": str(round(random.uniform(3.8, 4.8), 1)), "unit": "g/dL", "reference_range": "3.5-5.0", "is_abnormal": False},
        {"parameter_name": "Globulin", "value": str(round(random.uniform(2.2, 3.2), 1)), "unit": "g/dL", "reference_range": "2.0-3.5", "is_abnormal": False},
    ],
    "Kidney Function Test (KFT)": lambda gender, abnormal: [
        {"parameter_name": "Urea", "value": str(random.randint(55, 90) if abnormal else random.randint(20, 40)), "unit": "mg/dL", "reference_range": "17-43" if gender == "Male" else "15-40", "is_abnormal": abnormal},
        {"parameter_name": "Creatinine", "value": str(round(random.uniform(1.8, 3.5) if abnormal else random.uniform(0.7, 1.2), 1)), "unit": "mg/dL", "reference_range": "0.7-1.3" if gender == "Male" else "0.6-1.1", "is_abnormal": abnormal},
        {"parameter_name": "Uric Acid", "value": str(round(random.uniform(3.8, 6.5), 1)), "unit": "mg/dL", "reference_range": "3.5-7.2" if gender == "Male" else "2.6-6.0", "is_abnormal": False},
        {"parameter_name": "BUN", "value": str(random.randint(8, 18)), "unit": "mg/dL", "reference_range": "7-20", "is_abnormal": False},
        {"parameter_name": "eGFR", "value": str(random.randint(35, 60) if abnormal else random.randint(90, 120)), "unit": "mL/min/1.73m2", "reference_range": ">90", "is_abnormal": abnormal},
    ],
    "Thyroid Profile": lambda gender, abnormal: [
        {"parameter_name": "T3 (Triiodothyronine)", "value": str(round(random.uniform(40, 70) if abnormal else random.uniform(85, 180), 1)), "unit": "ng/dL", "reference_range": "80-200", "is_abnormal": abnormal},
        {"parameter_name": "T4 (Thyroxine)", "value": str(round(random.uniform(2.0, 4.0) if abnormal else random.uniform(5.0, 11.0), 1)), "unit": "mcg/dL", "reference_range": "4.5-12.0", "is_abnormal": abnormal},
        {"parameter_name": "TSH", "value": str(round(random.uniform(8.0, 25.0) if abnormal else random.uniform(0.5, 3.5), 2)), "unit": "mIU/L", "reference_range": "0.4-4.0", "is_abnormal": abnormal},
    ],
    "Vitamin D (25-OH)": lambda gender, abnormal: [
        {"parameter_name": "Vitamin D (25-OH)", "value": str(round(random.uniform(8.0, 18.0) if abnormal else random.uniform(35, 70), 1)), "unit": "ng/mL", "reference_range": "30-100", "is_abnormal": abnormal},
    ],
    "Vitamin B12": lambda gender, abnormal: [
        {"parameter_name": "Vitamin B12", "value": str(random.randint(100, 180) if abnormal else random.randint(250, 700)), "unit": "pg/mL", "reference_range": "200-900", "is_abnormal": abnormal},
    ],
}

# Fallback: simple normal results for tests not in the map
def generic_results(test_params, gender, abnormal):
    results = []
    for p in test_params:
        ref = p.get("reference_range_male", "") if gender == "Male" else p.get("reference_range_female", "")
        results.append({
            "parameter_name": p["name"],
            "value": "Normal" if not abnormal else "Abnormal",
            "unit": p.get("unit", ""),
            "reference_range": ref,
            "is_abnormal": abnormal,
        })
    return results


TECHNICIANS = ["Ramesh Patil", "Anjali Mehta", "Sunil Kumar", "Priyanka Shah"]
PATHOLOGISTS = ["Dr. V.K. Sharma", "Dr. Meena Iyer", "Dr. R.S. Reddy"]

SAMPLE_PRIORITIES = ["routine", "routine", "routine", "urgent", "stat"]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    # Check if data already exists
    patient_count = await db.patients.count_documents({})
    if patient_count >= 10:
        print("Sample data already exists. Skipping.")
        client.close()
        return

    now = datetime.now(timezone.utc)

    # Insert patients
    patient_docs = []
    for p in PATIENTS:
        doc = {**p, "created_at": now - timedelta(days=random.randint(5, 60)), "updated_at": now}
        patient_docs.append(doc)
    result = await db.patients.insert_many(patient_docs)
    patient_ids = list(result.inserted_ids)
    print(f"Inserted {len(patient_ids)} patients.")

    # Get test types
    all_tests = await db.tests.find().to_list(100)
    if not all_tests:
        print("No tests found. Run the main app first to seed test types.")
        client.close()
        return

    test_map = {t["name"]: t for t in all_tests}
    test_list = list(all_tests)

    # Create 20 samples
    samples = []
    sample_counter = 0
    for i in range(20):
        patient_idx = i % len(patient_ids)
        patient = patient_docs[patient_idx]
        pid = patient_ids[patient_idx]

        # Pick 1-3 tests per sample
        num_tests = random.randint(1, 3)
        chosen_tests = random.sample(test_list, min(num_tests, len(test_list)))
        test_ids = [t["_id"] for t in chosen_tests]
        test_objects = [{"id": str(t["_id"]), "name": t["name"], "price": t.get("price", 0)} for t in chosen_tests]
        total_price = sum(t.get("price", 0) for t in chosen_tests)

        sample_counter += 1
        days_ago = random.randint(0, 14)
        created = now - timedelta(days=days_ago, hours=random.randint(0, 8))
        sample_id_str = f"SMP-{created.strftime('%Y%m%d')}-{sample_counter:04d}"

        status = random.choice(["collected", "processing", "completed", "completed", "completed"])
        sample_doc = {
            "sample_id": sample_id_str,
            "patient_id": pid,
            "patient_name": patient["name"],
            "patient_phone": patient.get("phone", ""),
            "test_ids": test_ids,
            "tests": test_objects,
            "total_price": total_price,
            "collected_by": random.choice(TECHNICIANS),
            "priority": random.choice(SAMPLE_PRIORITIES),
            "status": status,
            "created_at": created,
            "updated_at": created + timedelta(hours=random.randint(1, 6)),
        }
        samples.append(sample_doc)

    result = await db.samples.insert_many(samples)
    sample_ids = list(result.inserted_ids)
    print(f"Inserted {len(sample_ids)} samples.")

    # Create 20 reports (15 verified, 5 pending)
    reports = []
    report_counter = 0
    for i in range(20):
        sample_doc = samples[i]
        sample_oid = sample_ids[i]
        patient_idx = i % len(patient_ids)
        patient = patient_docs[patient_idx]
        pid = patient_ids[patient_idx]

        # Pick first test from the sample
        test_oid = sample_doc["test_ids"][0]
        test_obj = None
        for t in all_tests:
            if t["_id"] == test_oid:
                test_obj = t
                break
        if not test_obj:
            test_obj = all_tests[0]
            test_oid = test_obj["_id"]

        report_counter += 1
        created = sample_doc["created_at"] + timedelta(hours=random.randint(2, 12))
        report_number = f"LR-{created.strftime('%Y%m%d')}-{report_counter:04d}"

        # Generate results
        is_abnormal = i in [0, 3, 5, 8, 11, 14, 17]  # ~7 out of 20 abnormal
        gender = patient["gender"]
        test_name = test_obj["name"]

        if test_name in RESULT_GENERATORS:
            results = RESULT_GENERATORS[test_name](gender, is_abnormal)
        else:
            results = generic_results(test_obj.get("parameters", []), gender, is_abnormal)

        is_verified = i < 15
        technician = random.choice(TECHNICIANS)
        pathologist = random.choice(PATHOLOGISTS)

        report_doc = {
            "report_number": report_number,
            "sample_id": sample_oid,
            "sample_code": sample_doc["sample_id"],
            "test_id": test_oid,
            "test_name": test_obj["name"],
            "test_category": test_obj.get("category", ""),
            "patient_id": pid,
            "patient_name": patient["name"],
            "patient_age": patient["age"],
            "patient_gender": patient["gender"],
            "doctor_name": patient.get("doctor_name", ""),
            "results": results,
            "technician_name": technician,
            "notes": "",
            "status": "verified" if is_verified else "pending_verification",
            "created_at": created,
            "updated_at": created + timedelta(hours=1),
        }
        if is_verified:
            report_doc["pathologist_name"] = pathologist
            report_doc["verified_by"] = pathologist
            report_doc["verified_at"] = created + timedelta(hours=random.randint(1, 4))

        reports.append(report_doc)

    # Reset counter collections so unique indexes don't clash
    await db.counters.update_one({"_id": "sample"}, {"$set": {"seq": sample_counter}}, upsert=True)
    await db.counters.update_one({"_id": "report"}, {"$set": {"seq": report_counter}}, upsert=True)

    await db.reports.insert_many(reports)
    print(f"Inserted {len(reports)} reports (15 verified, 5 pending).")

    print("\nSample data seeded successfully!")
    print("Login: admin@lab.local / admin123")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
