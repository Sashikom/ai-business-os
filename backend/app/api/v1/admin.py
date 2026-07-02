from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, AccessToken

router = APIRouter(tags=["admin"])

_session_factory = None
_ADMIN_TELEGRAM_ID = 5236809587


def set_session_factory(sf):
    global _session_factory
    _session_factory = sf


def get_session() -> AsyncSession:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized")
    return _session_factory()


async def _verify_admin(telegram_id: int):
    """Проверяет, что запрос от админа."""
    if telegram_id != _ADMIN_TELEGRAM_ID:
        raise HTTPException(status_code=403, detail="Доступ запрещён. Только для администратора.")


class GenerateTokensRequest(BaseModel):
    count: int = 1
    duration_days: int = 30


@router.post("/generate-tokens")
async def generate_tokens(req: GenerateTokensRequest, telegram_id: int):
    """Генерация токенов доступа (только для админа)."""
    await _verify_admin(telegram_id)

    if req.count < 1 or req.count > 100:
        raise HTTPException(status_code=400, detail="Количество токенов: от 1 до 100")

    tokens = []
    async with get_session() as session:
        for _ in range(req.count):
            token_str = AccessToken.generate_token()
            token_obj = AccessToken(
                token=token_str,
                duration_days=req.duration_days,
            )
            session.add(token_obj)
            tokens.append(token_str)
        await session.commit()

    return {"ok": True, "tokens": tokens, "count": len(tokens)}


@router.get("/tokens")
async def list_tokens(telegram_id: int, used: int | None = None):
    """Список токенов (только для админа)."""
    await _verify_admin(telegram_id)

    async with get_session() as session:
        query = select(AccessToken).order_by(AccessToken.created_at.desc())
        if used is not None:
            query = query.where(AccessToken.is_used == used)
        result = await session.execute(query)
        tokens = result.scalars().all()

        return {
            "ok": True,
            "count": len(tokens),
            "tokens": [
                {
                    "token": t.token,
                    "duration_days": t.duration_days,
                    "is_used": bool(t.is_used),
                    "used_by": t.used_by_telegram_id,
                    "used_at": t.used_at.isoformat() if t.used_at else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in tokens
            ],
        }


@router.get("/users")
async def list_users(telegram_id: int):
    """Список пользователей (только для админа)."""
    await _verify_admin(telegram_id)

    async with get_session() as session:
        result = await session.execute(
            select(User).order_by(User.created_at.desc())
        )
        users = result.scalars().all()

        return {
            "ok": True,
            "count": len(users),
            "users": [
                {
                    "telegram_id": u.telegram_id,
                    "username": u.username,
                    "first_name": u.first_name,
                    "subscription_status": u.subscription_status.value,
                    "has_access": u.has_access,
                    "days_left": u.days_left,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
        }


@router.post("/block-user")
async def block_user(telegram_id: int, block_telegram_id: int):
    """Заблокировать пользователя (только для админа)."""
    await _verify_admin(telegram_id)

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == block_telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        from app.models import SubscriptionStatus
        user.subscription_status = SubscriptionStatus.EXPIRED
        user.access_expires_at = datetime.utcnow()
        await session.commit()

    return {"ok": True, "message": f"Пользователь {block_telegram_id} заблокирован"}
