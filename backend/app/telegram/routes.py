from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import User, AccessToken, SubscriptionStatus

router = APIRouter(tags=["telegram"])

# Session factory будет установлен при инициализации
_session_factory = None


def set_session_factory(sf):
    global _session_factory
    _session_factory = sf


def get_session() -> AsyncSession:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized")
    return _session_factory()


class RegisterRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class ActivateTokenRequest(BaseModel):
    telegram_id: int
    token: str


class UserInfoResponse(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str | None
    subscription_status: str
    has_access: bool
    days_left: int


@router.post("/register")
async def register_user(req: RegisterRequest):
    """Авто-регистрация нового пользователя со статусом DEMO."""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == req.telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Пользователь уже существует — обновим имя если нужно
            if req.username and user.username != req.username:
                user.username = req.username
            if req.first_name and user.first_name != req.first_name:
                user.first_name = req.first_name
            if req.last_name and user.last_name != req.last_name:
                user.last_name = req.last_name
            await session.commit()
            return {
                "ok": True,
                "is_new": False,
                "has_access": user.has_access,
                "days_left": user.days_left,
                "subscription_status": user.subscription_status.value,
            }

        # Новый пользователь — создаём с DEMO
        user = User(
            telegram_id=req.telegram_id,
            username=req.username,
            first_name=req.first_name,
            last_name=req.last_name,
            subscription_status=SubscriptionStatus.DEMO,
            demo_started_at=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        return {
            "ok": True,
            "is_new": True,
            "has_access": True,
            "days_left": 3,
            "subscription_status": "DEMO",
        }


@router.post("/activate-token")
async def activate_token(req: ActivateTokenRequest):
    """Активация токена доступа."""
    async with get_session() as session:
        # Ищем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == req.telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Ищем токен
        result = await session.execute(
            select(AccessToken).where(
                AccessToken.token == req.token,
                AccessToken.is_used == 0,
            )
        )
        token_obj = result.scalar_one_or_none()
        if not token_obj:
            raise HTTPException(status_code=400, detail="Токен не найден или уже использован")

        # Активируем токен
        token_obj.is_used = 1
        token_obj.used_by_telegram_id = req.telegram_id
        token_obj.used_at = datetime.utcnow()

        # Обновляем пользователя
        user.subscription_status = SubscriptionStatus.ACTIVE
        user.access_token = req.token
        user.access_expires_at = datetime.utcnow() + timedelta(days=token_obj.duration_days)

        await session.commit()

        return {
            "ok": True,
            "subscription_status": "ACTIVE",
            "days_left": token_obj.duration_days,
            "expires_at": user.access_expires_at.isoformat(),
        }


@router.get("/me")
async def get_me(telegram_id: int):
    """Информация о текущем пользователе."""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "subscription_status": user.subscription_status.value,
            "has_access": user.has_access,
            "days_left": user.days_left,
        }
