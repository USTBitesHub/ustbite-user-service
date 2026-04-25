from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import User
import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "ustbite-jwt-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class RegisterPayload(BaseModel):
    email: EmailStr
    employee_id: str
    name: str
    password: str
    phone: str | None = None
    department: str = "IT"
    floor_number: str | None = None


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,        # used by order-service for notification emails
        "employee_id": user.employee_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def user_to_dict(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "employee_id": user.employee_id,
        "name": user.name,
        "phone": user.phone,
        "department": user.department.value if user.department else None,
        "floor_number": user.floor_number,
    }


@router.post("/login")
async def login(payload: LoginPayload, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user)
    return {
        "data": {"token": token, "user": user_to_dict(user)},
        "message": "Login successful",
        "status": "success"
    }


@router.post("/register")
async def register(payload: RegisterPayload, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    result2 = await db.execute(
        select(User).where(User.employee_id == payload.employee_id)
    )
    if result2.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Employee ID already registered")

    from app.models.models import DepartmentEnum
    dept_map = {e.value.lower(): e for e in DepartmentEnum}
    dept = dept_map.get(payload.department.lower(), DepartmentEnum.IT)

    new_user = User(
        email=payload.email,
        employee_id=payload.employee_id,
        name=payload.name,
        phone=payload.phone,
        department=dept,
        floor_number=payload.floor_number,
        password_hash=hash_password(payload.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_token(new_user)
    return {
        "data": {"token": token, "user": user_to_dict(new_user)},
        "message": "Registered successfully",
        "status": "success"
    }


@router.post("/logout")
async def logout():
    # JWT is stateless — client just discards the token
    return {"message": "Logged out successfully", "status": "success"}
