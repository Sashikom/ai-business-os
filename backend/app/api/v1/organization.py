from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.core.database import get_db
from app.models import User, Organization, Membership

router = APIRouter()


@router.get("/")
async def list_organizations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization).join(Membership).where(Membership.user_id == current_user.id))
    orgs = result.scalars().all()
    return {"organizations": [{"id": str(o.id), "name": o.name, "subscription_status": o.subscription_status, "credits_balance": o.credits_balance, "credits_used": o.credits_used} for o in orgs]}
