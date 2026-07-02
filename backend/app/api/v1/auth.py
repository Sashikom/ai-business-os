from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models import User

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=get_password_hash(data.password), full_name=data.full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"access_token": create_access_token(user.id), "refresh_token": create_refresh_token(user.id), "token_type": "bearer"}


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account blocked")
    return {"access_token": create_access_token(user.id), "refresh_token": create_refresh_token(user.id), "token_type": "bearer"}
