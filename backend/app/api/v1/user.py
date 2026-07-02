from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models import User

router = APIRouter()


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email, "full_name": current_user.full_name, "is_active": current_user.is_active, "telegram_username": current_user.telegram_username}
