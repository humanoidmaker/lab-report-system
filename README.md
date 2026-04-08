# LabSync — Lab Report Management

Pathology lab management with test catalog, sample tracking, result entry, and verified report generation.

## Tech Stack

Python FastAPI + Motor (MongoDB) + React + TypeScript

## Features

- **20 pre-configured test types (CBC, Lipid Profile, Thyroid, etc.)**
- **Sample registration with unique SMP-ID generation**
- **Result entry with reference range comparison**
- **Auto-detection of abnormal values**
- **Report verification workflow**
- **Printable lab reports with abnormal highlights**
- **Patient management with history**
- **Dashboard with sample pipeline stats**

## Setup

### Using Docker (Recommended)

```bash
docker-compose up
```

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Set environment variables (copy .env.example to .env)
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Seed Data:**
```bash
cd backend
python -m scripts.seed_admin
python -m scripts.seed_sample_data
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URI / DATABASE_URL | Database connection string | localhost |
| JWT_SECRET | Secret key for JWT tokens | (required) |
| CORS_ORIGINS | Allowed frontend origins | http://localhost:3000 |
| SMTP_HOST | SMTP server for emails | (optional) |
| SMTP_PORT | SMTP port | 587 |
| SMTP_USER | SMTP username | (optional) |
| SMTP_PASS | SMTP password | (optional) |

## Default Login

- **Admin:** admin@lab.local / admin123

## License

MIT License — Copyright (c) 2026 Humanoid Maker (www.humanoidmaker.com)
