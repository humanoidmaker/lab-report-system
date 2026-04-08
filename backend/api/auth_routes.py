from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import users_col
from auth import hash_password, verify_password, create_token
from config import ADMIN_EMAIL, ADMIN_PASSWORD

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "user"


@router.on_event("startup")
async def seed_admin():
    existing = await users_col.find_one({"email": ADMIN_EMAIL})
    if not existing:
        await users_col.insert_one({
            "email": ADMIN_EMAIL,
            "password": hash_password(ADMIN_PASSWORD),
            "name": "Admin",
            "role": "admin",
        })


@router.post("/login")
async def login(req: LoginRequest):
    user = await users_col.find_one({"email": req.email})
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user["email"], "role": user["role"], "name": user["name"]})
    return {"token": token, "email": user["email"], "name": user["name"], "role": user["role"]}


@router.post("/register")
async def register(req: RegisterRequest):
    existing = await users_col.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    await users_col.insert_one({
        "email": req.email,
        "password": hash_password(req.password),
        "name": req.name,
        "role": req.role,
    })
    token = create_token({"sub": req.email, "role": req.role, "name": req.name})
    return {"token": token, "email": req.email, "name": req.name, "role": req.role}
