from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import uuid

from app.core.database import get_db
from app.models import User, Organization, AccessToken, Generation

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Импортируем Membership если есть, иначе используем raw SQL
try:
    from app.models import Membership
except ImportError:
    Membership = None


class RegisterRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ActivateTokenRequest(BaseModel):
    telegram_id: int
    token: str


class AIChatRequest(BaseModel):
    telegram_id: int
    message: str
    module: str = "chat"


async def get_user_org(db: AsyncSession, user_id: str):
    """Получить organization пользователя через memberships"""
    if Membership is not None:
        result = await db.execute(
            select(Membership).where(Membership.user_id == user_id)
        )
        membership = result.scalar_one_or_none()
        if membership:
            org_result = await db.execute(
                select(Organization).where(Organization.id == membership.organization_id)
            )
            return org_result.scalar_one_or_none()
    else:
        # Fallback на raw SQL
        from sqlalchemy import text
        result = await db.execute(
            text("SELECT organization_id FROM memberships WHERE user_id = :uid LIMIT 1"),
            {"uid": user_id}
        )
        row = result.first()
        if row:
            org_result = await db.execute(
                select(Organization).where(Organization.id == row[0])
            )
            return org_result.scalar_one_or_none()
    return None


async def create_membership(db: AsyncSession, user_id: str, org_id: str, role: str = "member"):
    """Создать membership"""
    if Membership is not None:
        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=org_id,
            role=role,
            created_at=datetime.utcnow()
        )
        db.add(membership)
    else:
        from sqlalchemy import text
        await db.execute(
            text("INSERT INTO memberships (id, user_id, organization_id, role, created_at) VALUES (:id, :uid, :oid, :role, :now)"),
            {"id": str(uuid.uuid4()), "uid": user_id, "oid": org_id, "role": role, "now": datetime.utcnow()}
        )


@router.get("/me")
async def get_me(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    
    org = await get_user_org(db, user.id)
    
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "is_superuser": getattr(user, 'is_superuser', False),
        "has_access": getattr(user, 'has_access', False),
        "days_left": getattr(user, 'days_left', 0) or 0,
        "subscription_status": user.subscription_status.value if hasattr(user.subscription_status, 'value') else str(user.subscription_status or "DEMO"),
        "credits_balance": org.credits_balance if org else 0,
        "credits_used": org.credits_used if org else 0,
    }


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли уже
    result = await db.execute(
        select(User).where(User.telegram_id == data.telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        return {"message": "already_exists", "user": await get_me(data.telegram_id, db)}
    
    # Создаём организацию
    org_id = str(uuid.uuid4())
    org = Organization(
        id=org_id,
        name=f"User_{data.telegram_id}",
        subscription_status="demo",
        credits_balance=500,
        credits_used=0,
        created_at=datetime.utcnow(),
    )
    db.add(org)
    await db.flush()
    
    # Создаём пользователя
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        telegram_id=data.telegram_id,
        username=data.username,
        full_name=data.first_name,
        subscription_status="DEMO",
        demo_started_at=datetime.utcnow(),
        is_active=True,
        has_access=True,
    )
    db.add(user)
    await db.flush()
    
    # Создаём membership
    await create_membership(db, user_id, org_id, role="owner")
    
    await db.commit()
    
    return {
        "message": "registered",
        "user": {
            "days_left": 3,
            "credits_balance": 500,
        }
    }


@router.post("/activate-token")
async def activate_token(data: ActivateTokenRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AccessToken).where(AccessToken.token == data.token)
    )
    access_token = result.scalar_one_or_none()
    
    if not access_token or access_token.is_used:
        raise HTTPException(status_code=400, detail="Неверный или использованный токен")
    
    user_result = await db.execute(
        select(User).where(User.telegram_id == data.telegram_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    access_token.is_used = True
    access_token.used_at = datetime.utcnow()
    access_token.used_by_telegram_id = data.telegram_id
    
    user.subscription_status = "ACTIVE"
    user.access_token = data.token
    user.access_expires_at = datetime.utcnow() + timedelta(days=access_token.duration_days)
    user.has_access = True
    
    await db.commit()
    
    return {
        "message": "Token activated",
        "days_left": access_token.duration_days,
    }


@router.post("/ai-chat")
async def ai_chat(data: AIChatRequest, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(
        select(User).where(User.telegram_id == data.telegram_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    org = await get_user_org(db, user.id)
    
    is_admin = getattr(user, 'is_superuser', False)
    if not is_admin and not getattr(user, 'has_access', False):
        raise HTTPException(status_code=403, detail="Доступ истёк")
    
    if not is_admin and org and org.credits_balance <= 0:
        raise HTTPException(status_code=403, detail="Закончились кредиты")
    
    from app.ai.groq_client import GroqClient
    groq = GroqClient()
    try:
        result_text = await groq.generate(data.message, module=data.module)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")
    
    if not is_admin and org:
        org.credits_balance -= 1
        org.credits_used += 1
    
    gen = Generation(
        user_id=user.id,
        module=data.module,
        prompt=data.message,
        result=result_text,
    )
    db.add(gen)
    await db.commit()
    
    return {
        "result": result_text,
        "credits_left": org.credits_balance if org and not is_admin else 999999,
    }
