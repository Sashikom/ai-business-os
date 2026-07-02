from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.organization import router as org_router
from app.api.v1.ai import router as ai_router
from app.api.v1.admin import router as admin_router
from app.api.v1.telegram import router as telegram_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(org_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(telegram_router, tags=["telegram"])
