"""
Seed script for LabSync - Lab Report Management System
Run: python seed_sample_data.py
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config import MONGODB_URL, DATABASE_NAME

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]


async def seed():
    # Clear existing data
    for col_name in ["tests", "patients", "samples", "reports", "counters"]:
        await db[col_name].delete_many({})

    print("Seeding tests...")
    tests_data = [
        {
            "name": "Complete Blood Count (CBC)",
            "category": "Hematology",
            "sample_type": "blood",
            "description": "Measures various blood cell components",
            "price": 350,
            "turnaround_hours": 4,
            "parameters": [
                {"name": "Hemoglobin", "unit": "g/dL", "reference_range_male": "13.5-17.5", "reference_range_female": "12.0-16.0"},
                {"name": "RBC Count", "unit": "million/uL", "reference_range_male": "4.7-6.1", "reference_range_female": "4.2-5.4"},
                {"name": "WBC Count", "unit": "/uL", "reference_range_male": "4500-11000", "reference_range_female": "4500-11000"},
                {"name": "Platelet Count", "unit": "/uL", "reference_range_male": "150000-400000", "reference_range_female": "150000-400000"},
                {"name": "PCV/Hematocrit", "unit": "%", "reference_range_male": "40-54", "reference_range_female": "36-48"},
                {"name": "MCV", "unit": "fL", "reference_range_male": "80-100", "reference_range_female": "80-100"},
                {"name": "MCH", "unit": "pg", "reference_range_male": "27-33", "reference_range_female": "27-33"},
                {"name": "MCHC", "unit": "g/dL", "reference_range_male": "32-36", "reference_range_female": "32-36"},
                {"name": "Neutrophils", "unit": "%", "reference_range_male": "40-70", "reference_range_female": "40-70"},
                {"name": "Lymphocytes", "unit": "%", "reference_range_male": "20-40", "reference_range_female": "20-40"},
            ],
        },
        {
            "name": "Blood Sugar Fasting",
            "category": "Biochemistry",
            "sample_type": "blood",
            "description": "Fasting blood glucose level",
            "price": 80,
            "turnaround_hours": 2,
            "parameters": [
                {"name": "Fasting Blood Sugar", "unit": "mg/dL", "reference_range_male": "70-100", "reference_range_female": "70-100"},
            ],
        },
        {
            "name": "Blood Sugar PP",
            "category": "Biochemistry",
            "sample_type": "blood",
            "description": "Post-prandial blood glucose level",
            "price": 80,
            "turnaround_hours": 2,
            "parameters": [
                {"name": "Post Prandial Blood Sugar", "unit": "mg/dL", "reference_range_male": "70-140", "reference_range_female": "70-140"},
            ],
        },
        {
            "name": "HbA1c",
            "category": "Biochemistry",
            "sample_type": "blood",
            "description": "Glycated hemoglobin test",
            "price": 450,
            "turnaround_hours": 6,
            "parameters": [
                {"name": "HbA1c", "unit": "%", "reference_range_male": "4.0-5.6", "reference_range_female": "4.0-5.6"},
            ],
        },
        {
            "name": "Lipid Profile",
            "category": "Lipid",
            "sample_type": "blood",
            "description": "Complete cholesterol panel",
            "price": 500,
            "turnaround_hours": 6,
            "parameters": [
                {"name": "Total Cholesterol", "unit": "mg/dL", "reference_range_male": "<200", "reference_range_female": "<200"},
                {"name": "Triglycerides", "unit": "mg/dL", "reference_range_male": "<150", "reference_range_female": "<150"},
                {"name": "HDL Cholesterol", "unit": "mg/dL", "reference_range_male": "40-60", "reference_range_female": "50-60"},
                {"name": "LDL Cholesterol", "unit": "mg/dL", "reference_range_male": "<100", "reference_range_female": "<100"},
                {"name": "VLDL Cholesterol", "unit": "mg/dL", "reference_range_male": "5-40", "reference_range_female": "5-40"},
                {"name": "TC/HDL Ratio", "unit": "", "reference_range_male": "<5.0", "reference_range_female": "<5.0"},
            ],
        },
        {
            "name": "Liver Function Test (LFT)",
            "category": "Liver",
            "sample_type": "blood",
            "description": "Comprehensive liver panel",
            "price": 600,
            "turnaround_hours": 6,
            "parameters": [
                {"name": "Total Bilirubin", "unit": "mg/dL", "reference_range_male": "0.1-1.2", "reference_range_female": "0.1-1.2"},
                {"name": "Direct Bilirubin", "unit": "mg/dL", "reference_range_male": "0.0-0.3", "reference_range_female": "0.0-0.3"},
                {"name": "Indirect Bilirubin", "unit": "mg/dL", "reference_range_male": "0.1-0.9", "reference_range_female": "0.1-0.9"},
                {"name": "SGOT (AST)", "unit": "U/L", "reference_range_male": "8-40", "reference_range_female": "8-40"},
                {"name": "SGPT (ALT)", "unit": "U/L", "reference_range_male": "7-56", "reference_range_female": "7-56"},
                {"name": "Alkaline Phosphatase", "unit": "U/L", "reference_range_male": "44-147", "reference_range_female": "44-147"},
                {"name": "Total Protein", "unit": "g/dL", "reference_range_male": "6.0-8.3", "reference_range_female": "6.0-8.3"},
                {"name": "Albumin", "unit": "g/dL", "reference_range_male": "3.5-5.5", "reference_range_female": "3.5-5.5"},
            ],
        },
        {
            "name": "Kidney Function Test (KFT)",
            "category": "Kidney",
            "sample_type": "blood",
            "description": "Renal function panel",
            "price": 550,
            "turnaround_hours": 6,
            "parameters": [
                {"name": "Blood Urea", "unit": "mg/dL", "reference_range_male": "7-20", "reference_range_female": "7-20"},
                {"name": "Serum Creatinine", "unit": "mg/dL", "reference_range_male": "0.7-1.3", "reference_range_female": "0.6-1.1"},
                {"name": "Uric Acid", "unit": "mg/dL", "reference_range_male": "3.4-7.0", "reference_range_female": "2.4-6.0"},
                {"name": "BUN", "unit": "mg/dL", "reference_range_male": "6-24", "reference_range_female": "6-24"},
                {"name": "BUN/Creatinine Ratio", "unit": "", "reference_range_male": "10-20", "reference_range_female": "10-20"},
            ],
        },
        {
            "name": "Thyroid Profile",
            "category": "Thyroid",
            "sample_type": "blood",
            "description": "T3, T4, and TSH levels",
            "price": 650,
            "turnaround_hours": 8,
            "parameters": [
                {"name": "T3 (Triiodothyronine)", "unit": "ng/dL", "reference_range_male": "80-200", "reference_range_female": "80-200"},
                {"name": "T4 (Thyroxine)", "unit": "ug/dL", "reference_range_male": "5.1-14.1", "reference_range_female": "5.1-14.1"},
                {"name": "TSH", "unit": "uIU/mL", "reference_range_male": "0.4-4.0", "reference_range_female": "0.4-4.0"},
            ],
        },
        {
            "name": "Urine Routine",
            "category": "Urine",
            "sample_type": "urine",
            "description": "Complete urine analysis",
            "price": 150,
            "turnaround_hours": 3,
            "parameters": [
                {"name": "Color", "unit": "", "reference_range_male": "Pale Yellow", "reference_range_female": "Pale Yellow"},
                {"name": "Appearance", "unit": "", "reference_range_male": "Clear", "reference_range_female": "Clear"},
                {"name": "pH", "unit": "", "reference_range_male": "4.5-8.0", "reference_range_female": "4.5-8.0"},
                {"name": "Specific Gravity", "unit": "", "reference_range_male": "1.005-1.030", "reference_range_female": "1.005-1.030"},
                {"name": "Protein", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                {"name": "Glucose", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                {"name": "Ketones", "unit": "", "reference_range_male": "Nil", "reference_range_female": "Nil"},
                {"name": "RBC", "unit": "/HPF", "reference_range_male": "0-2", "reference_range_female": "0-2"},
                {"name": "WBC (Pus Cells)", "unit": "/HPF", "reference_range_male": "0-5", "reference_range_female": "0-5"},
                {"name": "Epithelial Cells", "unit": "/HPF", "reference_range_male": "0-5", "reference_range_female": "0-5"},
            ],
        },
        {
            "name": "ESR",
            "category": "Hematology",
            "sample_type": "blood",
            "description": "Erythrocyte Sedimentation Rate",
            "price": 100,
            "turnaround_hours": 2,
            "parameters": [
                {"name": "ESR", "unit": "mm/hr", "reference_range_male": "0-15", "reference_range_female": "0-20"},
            ],
        },
        {
            "name": "CRP (C-Reactive Protein)",
            "category": "Immunology",
            "sample_type": "blood",
            "description": "Inflammation marker",
            "price": 400,
            "turnaround_hours": 4,
            "parameters": [
                {"name": "CRP", "unit": "mg/L", "reference_range_male": "<6.0", "reference_range_female": "<6.0"},
            ],
        },
        {
            "name": "Vitamin D (25-OH)",
            "category": "Biochemistry",
            "sample_type": "blood",
            "description": "Vitamin D levels",
            "price": 1200,
            "turnaround_hours": 24,
            "parameters": [
                {"name": "Vitamin D (25-Hydroxy)", "unit": "ng/mL", "reference_range_male": "30-100", "reference_range_female": "30-100"},
            ],
        },
        {
            "name": "Vitamin B12",
            "category": "Biochemistry",
            "sample_type": "blood",
            "description": "Cobalamin levels",
            "price": 800,
            "turnaround_hours": 24,
            "parameters": [
                {"name": "Vitamin B12", "unit": "pg/mL", "reference_range_male": "200-900", "reference_range_female": "200-900"},
            ],
        },
        {
            "name": "Iron Studies",
            "category": "Biochemistry",
            "sample_type": "blood",
            "description": "Serum iron, TIBC, Ferritin",
            "price": 700,
            "turnaround_hours": 8,
            "parameters": [
                {"name": "Serum Iron", "unit": "ug/dL", "reference_range_male": "60-170", "reference_range_female": "50-170"},
                {"name": "TIBC", "unit": "ug/dL", "reference_range_male": "250-370", "reference_range_female": "250-370"},
                {"name": "Ferritin", "unit": "ng/mL", "reference_range_male": "20-250", "reference_range_female": "10-120"},
            ],
        },
        {
            "name": "Serology (HIV/HBsAg)",
            "category": "Immunology",
            "sample_type": "blood",
            "description": "HIV and Hepatitis B screening",
            "price": 600,
            "turnaround_hours": 6,
            "parameters": [
                {"name": "HIV I & II", "unit": "", "reference_range_male": "Non-Reactive", "reference_range_female": "Non-Reactive"},
                {"name": "HBsAg", "unit": "", "reference_range_male": "Non-Reactive", "reference_range_female": "Non-Reactive"},
            ],
        },
        {
            "name": "Blood Group",
            "category": "Hematology",
            "sample_type": "blood",
            "description": "ABO and Rh typing",
            "price": 150,
            "turnaround_hours": 1,
            "parameters": [
                {"name": "Blood Group", "unit": "", "reference_range_male": "A/B/AB/O", "reference_range_female": "A/B/AB/O"},
                {"name": "Rh Factor", "unit": "", "reference_range_male": "Positive/Negative", "reference_range_female": "Positive/Negative"},
            ],
        },
        {
            "name": "Widal Test",
            "category": "Microbiology",
            "sample_type": "blood",
            "description": "Typhoid fever screening",
            "price": 250,
            "turnaround_hours": 4,
            "parameters": [
                {"name": "S. Typhi O", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                {"name": "S. Typhi H", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                {"name": "S. Paratyphi AH", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
                {"name": "S. Paratyphi BH", "unit": "", "reference_range_male": "<1:80", "reference_range_female": "<1:80"},
            ],
        },
        {
            "name": "Dengue NS1 Antigen",
            "category": "Immunology",
            "sample_type": "blood",
            "description": "Dengue early detection",
            "price": 800,
            "turnaround_hours": 4,
            "parameters": [
                {"name": "Dengue NS1 Antigen", "unit": "", "reference_range_male": "Negative", "reference_range_female": "Negative"},
            ],
        },
        {
            "name": "Malaria Rapid Test",
            "category": "Microbiology",
            "sample_type": "blood",
            "description": "Malaria parasite detection",
            "price": 350,
            "turnaround_hours": 2,
            "parameters": [
                {"name": "P. Vivax", "unit": "", "reference_range_male": "Negative", "reference_range_female": "Negative"},
                {"name": "P. Falciparum", "unit": "", "reference_range_male": "Negative", "reference_range_female": "Negative"},
            ],
        },
        {
            "name": "COVID-19 RT-PCR",
            "category": "Microbiology",
            "sample_type": "swab",
            "description": "SARS-CoV-2 detection by RT-PCR",
            "price": 500,
            "turnaround_hours": 24,
            "parameters": [
                {"name": "SARS-CoV-2 RNA", "unit": "", "reference_range_male": "Not Detected", "reference_range_female": "Not Detected"},
            ],
        },
    ]

    now = datetime.utcnow()
    for t in tests_data:
        t["created_at"] = now
        t["updated_at"] = now

    result = await db["tests"].insert_many(tests_data)
    test_ids = result.inserted_ids
    test_map = {tests_data[i]["name"]: test_ids[i] for i in range(len(test_ids))}
    print(f"  Inserted {len(test_ids)} tests")

    # Seed patients
    print("Seeding patients...")
    patients_data = [
        {"name": "Rajesh Kumar", "age": 45, "gender": "Male", "phone": "9876543210", "email": "rajesh@email.com", "doctor_name": "Dr. Sharma", "doctor_phone": "9876500001", "address": "123 MG Road, Mumbai"},
        {"name": "Priya Patel", "age": 32, "gender": "Female", "phone": "9876543211", "email": "priya@email.com", "doctor_name": "Dr. Gupta", "doctor_phone": "9876500002", "address": "45 Nehru Street, Delhi"},
        {"name": "Amit Singh", "age": 28, "gender": "Male", "phone": "9876543212", "email": "amit@email.com", "doctor_name": "Dr. Reddy", "doctor_phone": "9876500003", "address": "78 Park Avenue, Bangalore"},
        {"name": "Sunita Devi", "age": 55, "gender": "Female", "phone": "9876543213", "email": "sunita@email.com", "doctor_name": "Dr. Sharma", "doctor_phone": "9876500001", "address": "12 Lake View, Pune"},
        {"name": "Mohammed Ali", "age": 38, "gender": "Male", "phone": "9876543214", "email": "ali@email.com", "doctor_name": "Dr. Khan", "doctor_phone": "9876500004", "address": "34 Hill Road, Hyderabad"},
        {"name": "Kavita Nair", "age": 42, "gender": "Female", "phone": "9876543215", "email": "kavita@email.com", "doctor_name": "Dr. Menon", "doctor_phone": "9876500005", "address": "56 Sea Face, Kochi"},
        {"name": "Suresh Rao", "age": 60, "gender": "Male", "phone": "9876543216", "email": "suresh@email.com", "doctor_name": "Dr. Joshi", "doctor_phone": "9876500006", "address": "89 Temple Street, Chennai"},
        {"name": "Anita Sharma", "age": 25, "gender": "Female", "phone": "9876543217", "email": "anita@email.com", "doctor_name": "Dr. Gupta", "doctor_phone": "9876500002", "address": "23 Garden Colony, Jaipur"},
        {"name": "Vikram Malhotra", "age": 50, "gender": "Male", "phone": "9876543218", "email": "vikram@email.com", "doctor_name": "Dr. Kapoor", "doctor_phone": "9876500007", "address": "67 Civil Lines, Lucknow"},
        {"name": "Deepa Krishnan", "age": 35, "gender": "Female", "phone": "9876543219", "email": "deepa@email.com", "doctor_name": "Dr. Menon", "doctor_phone": "9876500005", "address": "41 Beach Road, Trivandrum"},
        {"name": "Ravi Verma", "age": 47, "gender": "Male", "phone": "9876543220", "email": "ravi@email.com", "doctor_name": "Dr. Singh", "doctor_phone": "9876500008", "address": "90 Station Road, Bhopal"},
        {"name": "Meena Joshi", "age": 30, "gender": "Female", "phone": "9876543221", "email": "meena@email.com", "doctor_name": "Dr. Joshi", "doctor_phone": "9876500006", "address": "15 Market Street, Nagpur"},
        {"name": "Arjun Deshmukh", "age": 22, "gender": "Male", "phone": "9876543222", "email": "arjun@email.com", "doctor_name": "Dr. Reddy", "doctor_phone": "9876500003", "address": "33 College Road, Pune"},
        {"name": "Lakshmi Iyer", "age": 65, "gender": "Female", "phone": "9876543223", "email": "lakshmi@email.com", "doctor_name": "Dr. Sharma", "doctor_phone": "9876500001", "address": "72 Gandhi Nagar, Chennai"},
        {"name": "Karan Mehta", "age": 33, "gender": "Male", "phone": "9876543224", "email": "karan@email.com", "doctor_name": "Dr. Khan", "doctor_phone": "9876500004", "address": "58 Link Road, Mumbai"},
    ]

    for p in patients_data:
        p["created_at"] = now
        p["updated_at"] = now

    pat_result = await db["patients"].insert_many(patients_data)
    patient_ids = pat_result.inserted_ids
    print(f"  Inserted {len(patient_ids)} patients")

    # Seed samples
    print("Seeding samples...")
    sample_assignments = [
        (0, ["Complete Blood Count (CBC)"], "collected"),
        (1, ["Thyroid Profile"], "collected"),
        (2, ["Blood Sugar Fasting", "HbA1c"], "collected"),
        (3, ["Lipid Profile"], "processing"),
        (4, ["Liver Function Test (LFT)"], "processing"),
        (5, ["Kidney Function Test (KFT)"], "processing"),
        (6, ["Complete Blood Count (CBC)", "ESR"], "completed"),
        (7, ["Urine Routine"], "completed"),
        (8, ["Vitamin D (25-OH)"], "completed"),
        (9, ["Iron Studies"], "completed"),
        (10, ["Serology (HIV/HBsAg)"], "completed"),
        (11, ["Blood Group"], "completed"),
        (12, ["Widal Test"], "completed"),
        (13, ["Dengue NS1 Antigen"], "completed"),
        (14, ["COVID-19 RT-PCR"], "completed"),
        (0, ["Lipid Profile", "Liver Function Test (LFT)"], "completed"),
        (1, ["Complete Blood Count (CBC)"], "completed"),
        (3, ["Thyroid Profile", "Blood Sugar Fasting"], "completed"),
        (5, ["Vitamin B12"], "completed"),
        (7, ["CRP (C-Reactive Protein)"], "completed"),
    ]

    sample_docs = []
    for i, (pat_idx, test_names, status) in enumerate(sample_assignments):
        tids = [test_map[tn] for tn in test_names]
        tests_info = [{"id": str(test_map[tn]), "name": tn, "price": next(t["price"] for t in tests_data if t["name"] == tn)} for tn in test_names]
        total_price = sum(t["price"] for t in tests_info)
        created = now - timedelta(days=20 - i, hours=i)
        sample_docs.append({
            "sample_id": f"SMP-{created.strftime('%Y%m%d')}-{i+1:04d}",
            "patient_id": patient_ids[pat_idx],
            "patient_name": patients_data[pat_idx]["name"],
            "patient_phone": patients_data[pat_idx]["phone"],
            "test_ids": tids,
            "tests": tests_info,
            "total_price": total_price,
            "collected_by": "Lab Tech 1" if i % 2 == 0 else "Lab Tech 2",
            "priority": "urgent" if i % 5 == 0 else "routine",
            "status": status,
            "created_at": created,
            "updated_at": created,
        })

    smp_result = await db["samples"].insert_many(sample_docs)
    sample_ids = smp_result.inserted_ids
    print(f"  Inserted {len(sample_ids)} samples")

    # Seed reports (for completed samples)
    print("Seeding reports...")
    report_docs = []
    report_counter = 0

    # Generate realistic results
    def gen_cbc_results(gender):
        is_m = gender == "Male"
        return [
            {"parameter_name": "Hemoglobin", "value": "14.2" if is_m else "11.5", "unit": "g/dL", "reference_range": "13.5-17.5" if is_m else "12.0-16.0", "is_abnormal": False if is_m else True},
            {"parameter_name": "RBC Count", "value": "5.1", "unit": "million/uL", "reference_range": "4.7-6.1" if is_m else "4.2-5.4", "is_abnormal": False},
            {"parameter_name": "WBC Count", "value": "7500", "unit": "/uL", "reference_range": "4500-11000", "is_abnormal": False},
            {"parameter_name": "Platelet Count", "value": "250000", "unit": "/uL", "reference_range": "150000-400000", "is_abnormal": False},
            {"parameter_name": "PCV/Hematocrit", "value": "42", "unit": "%", "reference_range": "40-54" if is_m else "36-48", "is_abnormal": False},
            {"parameter_name": "MCV", "value": "88", "unit": "fL", "reference_range": "80-100", "is_abnormal": False},
            {"parameter_name": "MCH", "value": "29", "unit": "pg", "reference_range": "27-33", "is_abnormal": False},
            {"parameter_name": "MCHC", "value": "34", "unit": "g/dL", "reference_range": "32-36", "is_abnormal": False},
            {"parameter_name": "Neutrophils", "value": "62", "unit": "%", "reference_range": "40-70", "is_abnormal": False},
            {"parameter_name": "Lymphocytes", "value": "30", "unit": "%", "reference_range": "20-40", "is_abnormal": False},
        ]

    results_map = {
        "Complete Blood Count (CBC)": lambda g: gen_cbc_results(g),
        "Blood Sugar Fasting": lambda g: [{"parameter_name": "Fasting Blood Sugar", "value": "126", "unit": "mg/dL", "reference_range": "70-100", "is_abnormal": True}],
        "Blood Sugar PP": lambda g: [{"parameter_name": "Post Prandial Blood Sugar", "value": "165", "unit": "mg/dL", "reference_range": "70-140", "is_abnormal": True}],
        "HbA1c": lambda g: [{"parameter_name": "HbA1c", "value": "6.8", "unit": "%", "reference_range": "4.0-5.6", "is_abnormal": True}],
        "Lipid Profile": lambda g: [
            {"parameter_name": "Total Cholesterol", "value": "220", "unit": "mg/dL", "reference_range": "<200", "is_abnormal": True},
            {"parameter_name": "Triglycerides", "value": "180", "unit": "mg/dL", "reference_range": "<150", "is_abnormal": True},
            {"parameter_name": "HDL Cholesterol", "value": "45", "unit": "mg/dL", "reference_range": "40-60", "is_abnormal": False},
            {"parameter_name": "LDL Cholesterol", "value": "130", "unit": "mg/dL", "reference_range": "<100", "is_abnormal": True},
            {"parameter_name": "VLDL Cholesterol", "value": "36", "unit": "mg/dL", "reference_range": "5-40", "is_abnormal": False},
            {"parameter_name": "TC/HDL Ratio", "value": "4.9", "unit": "", "reference_range": "<5.0", "is_abnormal": False},
        ],
        "Liver Function Test (LFT)": lambda g: [
            {"parameter_name": "Total Bilirubin", "value": "0.8", "unit": "mg/dL", "reference_range": "0.1-1.2", "is_abnormal": False},
            {"parameter_name": "Direct Bilirubin", "value": "0.2", "unit": "mg/dL", "reference_range": "0.0-0.3", "is_abnormal": False},
            {"parameter_name": "Indirect Bilirubin", "value": "0.6", "unit": "mg/dL", "reference_range": "0.1-0.9", "is_abnormal": False},
            {"parameter_name": "SGOT (AST)", "value": "55", "unit": "U/L", "reference_range": "8-40", "is_abnormal": True},
            {"parameter_name": "SGPT (ALT)", "value": "68", "unit": "U/L", "reference_range": "7-56", "is_abnormal": True},
            {"parameter_name": "Alkaline Phosphatase", "value": "95", "unit": "U/L", "reference_range": "44-147", "is_abnormal": False},
            {"parameter_name": "Total Protein", "value": "7.2", "unit": "g/dL", "reference_range": "6.0-8.3", "is_abnormal": False},
            {"parameter_name": "Albumin", "value": "4.1", "unit": "g/dL", "reference_range": "3.5-5.5", "is_abnormal": False},
        ],
        "Kidney Function Test (KFT)": lambda g: [
            {"parameter_name": "Blood Urea", "value": "18", "unit": "mg/dL", "reference_range": "7-20", "is_abnormal": False},
            {"parameter_name": "Serum Creatinine", "value": "1.0", "unit": "mg/dL", "reference_range": "0.7-1.3" if g == "Male" else "0.6-1.1", "is_abnormal": False},
            {"parameter_name": "Uric Acid", "value": "5.5", "unit": "mg/dL", "reference_range": "3.4-7.0" if g == "Male" else "2.4-6.0", "is_abnormal": False},
            {"parameter_name": "BUN", "value": "15", "unit": "mg/dL", "reference_range": "6-24", "is_abnormal": False},
            {"parameter_name": "BUN/Creatinine Ratio", "value": "15", "unit": "", "reference_range": "10-20", "is_abnormal": False},
        ],
        "Thyroid Profile": lambda g: [
            {"parameter_name": "T3 (Triiodothyronine)", "value": "140", "unit": "ng/dL", "reference_range": "80-200", "is_abnormal": False},
            {"parameter_name": "T4 (Thyroxine)", "value": "8.5", "unit": "ug/dL", "reference_range": "5.1-14.1", "is_abnormal": False},
            {"parameter_name": "TSH", "value": "6.2", "unit": "uIU/mL", "reference_range": "0.4-4.0", "is_abnormal": True},
        ],
        "Urine Routine": lambda g: [
            {"parameter_name": "Color", "value": "Pale Yellow", "unit": "", "reference_range": "Pale Yellow", "is_abnormal": False},
            {"parameter_name": "Appearance", "value": "Clear", "unit": "", "reference_range": "Clear", "is_abnormal": False},
            {"parameter_name": "pH", "value": "6.0", "unit": "", "reference_range": "4.5-8.0", "is_abnormal": False},
            {"parameter_name": "Specific Gravity", "value": "1.020", "unit": "", "reference_range": "1.005-1.030", "is_abnormal": False},
            {"parameter_name": "Protein", "value": "Nil", "unit": "", "reference_range": "Nil", "is_abnormal": False},
            {"parameter_name": "Glucose", "value": "Trace", "unit": "", "reference_range": "Nil", "is_abnormal": True},
            {"parameter_name": "Ketones", "value": "Nil", "unit": "", "reference_range": "Nil", "is_abnormal": False},
            {"parameter_name": "RBC", "value": "1", "unit": "/HPF", "reference_range": "0-2", "is_abnormal": False},
            {"parameter_name": "WBC (Pus Cells)", "value": "3", "unit": "/HPF", "reference_range": "0-5", "is_abnormal": False},
            {"parameter_name": "Epithelial Cells", "value": "2", "unit": "/HPF", "reference_range": "0-5", "is_abnormal": False},
        ],
        "ESR": lambda g: [{"parameter_name": "ESR", "value": "25", "unit": "mm/hr", "reference_range": "0-15" if g == "Male" else "0-20", "is_abnormal": True}],
        "Vitamin D (25-OH)": lambda g: [{"parameter_name": "Vitamin D (25-Hydroxy)", "value": "18", "unit": "ng/mL", "reference_range": "30-100", "is_abnormal": True}],
        "Iron Studies": lambda g: [
            {"parameter_name": "Serum Iron", "value": "55", "unit": "ug/dL", "reference_range": "60-170" if g == "Male" else "50-170", "is_abnormal": True if g == "Male" else False},
            {"parameter_name": "TIBC", "value": "380", "unit": "ug/dL", "reference_range": "250-370", "is_abnormal": True},
            {"parameter_name": "Ferritin", "value": "15", "unit": "ng/mL", "reference_range": "20-250" if g == "Male" else "10-120", "is_abnormal": True if g == "Male" else False},
        ],
        "Serology (HIV/HBsAg)": lambda g: [
            {"parameter_name": "HIV I & II", "value": "Non-Reactive", "unit": "", "reference_range": "Non-Reactive", "is_abnormal": False},
            {"parameter_name": "HBsAg", "value": "Non-Reactive", "unit": "", "reference_range": "Non-Reactive", "is_abnormal": False},
        ],
        "Blood Group": lambda g: [
            {"parameter_name": "Blood Group", "value": "B", "unit": "", "reference_range": "A/B/AB/O", "is_abnormal": False},
            {"parameter_name": "Rh Factor", "value": "Positive", "unit": "", "reference_range": "Positive/Negative", "is_abnormal": False},
        ],
        "Widal Test": lambda g: [
            {"parameter_name": "S. Typhi O", "value": "1:160", "unit": "", "reference_range": "<1:80", "is_abnormal": True},
            {"parameter_name": "S. Typhi H", "value": "1:80", "unit": "", "reference_range": "<1:80", "is_abnormal": False},
            {"parameter_name": "S. Paratyphi AH", "value": "<1:80", "unit": "", "reference_range": "<1:80", "is_abnormal": False},
            {"parameter_name": "S. Paratyphi BH", "value": "<1:80", "unit": "", "reference_range": "<1:80", "is_abnormal": False},
        ],
        "Dengue NS1 Antigen": lambda g: [{"parameter_name": "Dengue NS1 Antigen", "value": "Positive", "unit": "", "reference_range": "Negative", "is_abnormal": True}],
        "COVID-19 RT-PCR": lambda g: [{"parameter_name": "SARS-CoV-2 RNA", "value": "Not Detected", "unit": "", "reference_range": "Not Detected", "is_abnormal": False}],
        "Vitamin B12": lambda g: [{"parameter_name": "Vitamin B12", "value": "180", "unit": "pg/mL", "reference_range": "200-900", "is_abnormal": True}],
        "CRP (C-Reactive Protein)": lambda g: [{"parameter_name": "CRP", "value": "12.5", "unit": "mg/L", "reference_range": "<6.0", "is_abnormal": True}],
        "Malaria Rapid Test": lambda g: [
            {"parameter_name": "P. Vivax", "value": "Negative", "unit": "", "reference_range": "Negative", "is_abnormal": False},
            {"parameter_name": "P. Falciparum", "value": "Negative", "unit": "", "reference_range": "Negative", "is_abnormal": False},
        ],
    }

    completed_samples = [s for s in range(len(sample_assignments)) if sample_assignments[s][2] == "completed"]
    for i, smp_idx in enumerate(completed_samples):
        pat_idx, test_names, _ = sample_assignments[smp_idx]
        gender = patients_data[pat_idx]["gender"]
        for test_name in test_names:
            report_counter += 1
            created = sample_docs[smp_idx]["created_at"] + timedelta(hours=4)
            is_verified = report_counter <= 15
            doc = {
                "report_number": f"LR-{created.strftime('%Y%m%d')}-{report_counter:04d}",
                "sample_id": sample_ids[smp_idx],
                "sample_code": sample_docs[smp_idx]["sample_id"],
                "test_id": test_map[test_name],
                "test_name": test_name,
                "test_category": next(t["category"] for t in tests_data if t["name"] == test_name),
                "patient_id": patient_ids[pat_idx],
                "patient_name": patients_data[pat_idx]["name"],
                "patient_age": patients_data[pat_idx]["age"],
                "patient_gender": gender,
                "doctor_name": patients_data[pat_idx]["doctor_name"],
                "results": results_map.get(test_name, lambda g: [])(gender),
                "technician_name": "Tech. Ramesh" if report_counter % 2 == 0 else "Tech. Sunil",
                "notes": "Values slightly elevated, recommend follow-up" if report_counter % 3 == 0 else "",
                "status": "verified" if is_verified else "pending_verification",
                "created_at": created,
                "updated_at": created,
            }
            if is_verified:
                doc["pathologist_name"] = "Dr. Pathak"
                doc["verified_at"] = created + timedelta(hours=2)
            report_docs.append(doc)

    if report_docs:
        await db["reports"].insert_many(report_docs)
    print(f"  Inserted {len(report_docs)} reports")

    # Set counters
    await db["counters"].insert_many([
        {"_id": "sample", "seq": 25},
        {"_id": "report", "seq": report_counter + 1},
    ])

    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
