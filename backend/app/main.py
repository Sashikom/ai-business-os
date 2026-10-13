import os
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="AI Business OS Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq клиент
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
print(f"AI client initialized: model={MODEL_NAME}")

# === ИМИТАЦИЯ БАЗЫ ДАННЫХ (в памяти) ===
# В продакшене заменим на PostgreSQL
users_db = [
    {
        "id": 1,
        "telegram_id": 5236809587,
        "username": "Алекс Мак",
        "email": "alex@example.com",
        "subscription": "PRO",
        "status": "active",
        "created_at": "2026-09-01",
        "expires_at": "2026-11-01",
        "requests_used": 247,
        "requests_limit": 1000,
    },
    {
        "id": 2,
        "telegram_id": 123456789,
        "username": "Мария Иванова",
        "email": "maria@example.com",
        "subscription": "BASIC",
        "status": "active",
        "created_at": "2026-09-15",
        "expires_at": "2026-10-15",
        "requests_used": 89,
        "requests_limit": 100,
    },
    {
        "id": 3,
        "telegram_id": 987654321,
        "username": "Дмитрий Петров",
        "email": "dmitry@example.com",
        "subscription": "PRO",
        "status": "blocked",
        "created_at": "2026-08-20",
        "expires_at": "2026-10-20",
        "requests_used": 512,
        "requests_limit": 1000,
    },
]

tokens_db = [
    {
        "id": 1,
        "token": "AIBOS-A1B2C3D4-E5F6G7H8",
        "user_id": 1,
        "username": "Алекс Мак",
        "status": "active",
        "created_at": "2026-09-01",
        "expires_at": "2026-11-01",
        "used_at": None,
    },
    {
        "id": 2,
        "token": "AIBOS-X9Y8Z7W6-V5U4T3S2",
        "user_id": 2,
        "username": "Мария Иванова",
        "status": "active",
        "created_at": "2026-09-15",
        "expires_at": "2026-10-15",
        "used_at": "2026-09-15",
    },
]

payments_db = [
    {"id": 1, "user_id": 1, "amount": 2990, "status": "paid", "date": "2026-09-01", "plan": "PRO"},
    {"id": 2, "user_id": 2, "amount": 990, "status": "paid", "date": "2026-09-15", "plan": "BASIC"},
    {"id": 3, "user_id": 1, "amount": 2990, "status": "paid", "date": "2026-08-01", "plan": "PRO"},
]

# === МОДЕЛИ ===
class ChatRequest(BaseModel):
    telegram_id: int
    message: str
    module: str = "chat"

class ChatResponse(BaseModel):
    response: str
    module: str

class TokenGenerateRequest(BaseModel):
    subscription: str = "BASIC"  # BASIC, PRO, ENTERPRISE
    days_valid: int = 30
    username: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    subscription: str
    days_valid: int
    expires_at: str

class UserToggleRequest(BaseModel):
    status: str  # active, blocked

# === СИСТЕМНЫЕ ПРОМПТЫ ===
SYSTEM_PROMPTS = {
    "chat": "You are a business AI assistant. Reply in Russian with practical advice.",
    "market_research": "You are a market research expert. Reply in Russian with structured analysis.",
    "content": "You are a content creation expert. Reply in Russian with ready-to-use texts.",
    "funnel": "You are a sales funnel expert. Reply in Russian with concrete schemes and texts.",
}

# === AI CHAT ===
@app.post("/api/v1/ai/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest):
    import os
    import httpx
    
    system_prompt = SYSTEM_PROMPTS.get(req.module, SYSTEM_PROMPTS["chat"])
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    
    # ЖЁСТКИЙ ПРЯМОЙ URL. Никаких base_url из конфига, чтобы избежать дублирования /openai/v1
    target_url = "https://api.groq.com/openai/v1/chat/completions"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                target_url,
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": req.message},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 800,
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data["choices"][0]["message"]["content"]
                return ChatResponse(response=response_text, module=req.module)
            else:
                # Возвращаем реальную ошибку от Groq, чтобы мы её видели в логах
                raise HTTPException(status_code=response.status_code, detail=f"Groq API error: {response.text}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

@app.get("/api/v1/telegram/me")
async def get_me(telegram_id: int):
    return {"telegram_id": telegram_id, "has_access": True, "subscription_status": "ACTIVE", "days_left": 30}

# === АДМИНКА: СТАТИСТИКА ===
@app.get("/api/v1/admin/stats")
async def get_stats():
    total_users = len(users_db)
    active_users = len([u for u in users_db if u["status"] == "active"])
    total_tokens = len(tokens_db)
    active_tokens = len([t for t in tokens_db if t["status"] == "active"])
    total_revenue = sum(p["amount"] for p in payments_db if p["status"] == "paid")
    total_requests = sum(u["requests_used"] for u in users_db)
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_tokens": total_tokens,
        "active_tokens": active_tokens,
        "total_revenue": total_revenue,
        "total_requests": total_requests,
        "monthly_growth": 15,
    }

# === АДМИНКА: ПОЛЬЗОВАТЕЛИ ===
@app.get("/api/v1/admin/users")
async def get_users(status: Optional[str] = None):
    if status:
        return [u for u in users_db if u["status"] == status]
    return users_db

@app.put("/api/v1/admin/users/{user_id}/toggle")
async def toggle_user(user_id: int, req: UserToggleRequest):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["status"] = req.status
    return {"success": True, "user": user}

@app.put("/api/v1/admin/users/{user_id}/extend")
async def extend_user(user_id: int, days: int = 30):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["expires_at"] = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    return {"success": True, "user": user}

@app.delete("/api/v1/admin/users/{user_id}")
async def delete_user(user_id: int):
    global users_db
    users_db = [u for u in users_db if u["id"] != user_id]
    return {"success": True}

# === АДМИНКА: ТОКЕНЫ ===
def generate_token_code() -> str:
    """Генерирует токен формата AIBOS-XXXXXXXX-XXXXXXXX"""
    part1 = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
    part2 = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
    return f"AIBOS-{part1}-{part2}"

@app.get("/api/v1/admin/tokens")
async def get_tokens(status: Optional[str] = None):
    if status:
        return [t for t in tokens_db if t["status"] == status]
    return tokens_db

@app.post("/api/v1/admin/tokens/generate", response_model=TokenResponse)
async def generate_token(req: TokenGenerateRequest):
    token_code = generate_token_code()
    expires_at = (datetime.now() + timedelta(days=req.days_valid)).strftime("%Y-%m-%d")
    
    new_token = {
        "id": len(tokens_db) + 1,
        "token": token_code,
        "user_id": None,
        "username": req.username or "Не назначен",
        "status": "active",
        "subscription": req.subscription,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "expires_at": expires_at,
        "used_at": None,
    }
    tokens_db.append(new_token)
    
    return TokenResponse(
        token=token_code,
        subscription=req.subscription,
        days_valid=req.days_valid,
        expires_at=expires_at,
    )

@app.post("/api/v1/admin/tokens/{token_id}/revoke")
async def revoke_token(token_id: int):
    token = next((t for t in tokens_db if t["id"] == token_id), None)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    token["status"] = "revoked"
    return {"success": True}

@app.delete("/api/v1/admin/tokens/{token_id}")
async def delete_token(token_id: int):
    global tokens_db
    tokens_db = [t for t in tokens_db if t["id"] != token_id]
    return {"success": True}

# === АДМИНКА: ПЛАТЕЖИ ===
@app.get("/api/v1/admin/payments")
async def get_payments():
    return payments_db

@app.get("/api/v1/admin/plans")
async def get_plans():
    return [
        {"id": "BASIC", "name": "Базовый", "price": 990, "requests": 100, "features": ["AI Чат", "Воронки продаж"]},
        {"id": "PRO", "name": "Профессиональный", "price": 2990, "requests": 1000, "features": ["Все модули", "Приоритет", "API доступ"]},
        {"id": "ENTERPRISE", "name": "Корпоративный", "price": 9900, "requests": -1, "features": ["Безлимит", "White label", "Персональный менеджер"]},
    ]
 # === БОТ: АКТИВАЦИЯ ТОКЕНА ===
class TokenActivateRequest(BaseModel):
    telegram_id: int
    token: str
    username: Optional[str] = None

@app.post("/api/v1/bot/activate-token")
async def activate_token(req: TokenActivateRequest):
    """Активирует токен для Telegram-пользователя"""
    from datetime import datetime
    
    # Ищем токен в базе
    token_record = next((t for t in tokens_db if t["token"] == req.token), None)
    
    if not token_record:
        return {"success": False, "message": "❌ Токен не найден. Проверьте правильность ввода."}
    
    if token_record["status"] != "active":
        return {"success": False, "message": "⛔ Токен уже использован или отозван."}
    
    expires = datetime.strptime(token_record["expires_at"], "%Y-%m-%d")
    if expires < datetime.now():
        return {"success": False, "message": "⏰ Срок действия токена истёк."}
    
    # Определяем лимиты по тарифу
    limits = {
        "BASIC": 100,
        "PRO": 1000,
        "ENTERPRISE": -1  # безлимит
    }
    subscription = token_record.get("subscription", "BASIC")
    limit = limits.get(subscription, 100)
    
    # Создаём или обновляем пользователя
    user = next((u for u in users_db if u["telegram_id"] == req.telegram_id), None)
    
    if user:
        user["subscription"] = subscription
        user["status"] = "active"
        user["expires_at"] = token_record["expires_at"]
        user["requests_limit"] = limit
        user["requests_used"] = 0
    else:
        new_user = {
            "id": len(users_db) + 1,
            "telegram_id": req.telegram_id,
            "username": req.username or "Telegram User",
            "email": None,
            "subscription": subscription,
            "status": "active",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "expires_at": token_record["expires_at"],
            "requests_used": 0,
            "requests_limit": limit,
        }
        users_db.append(new_user)
        user = new_user
    
    # Помечаем токен как использованный
    token_record["status"] = "used"
    token_record["user_id"] = user["id"]
    token_record["username"] = user["username"]
    token_record["used_at"] = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "success": True,
        "message": f"✅ Доступ активирован!\n\nТариф: {subscription}\nЛимит запросов: {'∞ безлимит' if limit == -1 else limit}\nДействует до: {token_record['expires_at']}",
        "subscription": subscription,
        "expires_at": token_record["expires_at"],
        "requests_limit": limit,
    }

# === БОТ: ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ ===
@app.get("/api/v1/bot/check-user")
async def check_user(telegram_id: int):
    """Проверяет, авторизован ли пользователь"""
    from datetime import datetime
    
    user = next((u for u in users_db if u["telegram_id"] == telegram_id), None)
    
    if not user:
        return {"authorized": False, "message": "Пользователь не найден"}
    
    if user["status"] != "active":
        return {"authorized": False, "message": "Доступ заблокирован"}
    
    expires = datetime.strptime(user["expires_at"], "%Y-%m-%d")
    if expires < datetime.now():
        user["status"] = "expired"
        return {"authorized": False, "message": "Срок подписки истёк"}
    
    if user["requests_limit"] != -1 and user["requests_used"] >= user["requests_limit"]:
        return {
            "authorized": False, 
            "message": "Лимит запросов исчерпан. Продлите подписку.",
            "subscription": user["subscription"],
            "requests_used": user["requests_used"],
            "requests_limit": user["requests_limit"],
        }
    
    return {
        "authorized": True,
        "username": user["username"],
        "subscription": user["subscription"],
        "expires_at": user["expires_at"],
        "requests_used": user["requests_used"],
        "requests_limit": user["requests_limit"],
    }

# === БОТ: УВЕЛИЧЕНИЕ СЧЁТЧИКА ЗАПРОСОВ ===
@app.post("/api/v1/bot/increment-requests")
async def increment_requests(telegram_id: int):
    """Увеличивает счётчик использованных запросов"""
    user = next((u for u in users_db if u["telegram_id"] == telegram_id), None)
    if user and user["requests_limit"] != -1:
        user["requests_used"] += 1
    return {"success": True}
# === ЗАЯВКИ НА ДОСТУП (модерация с телефона) ===
PLANS = {
    "BASIC": 100,
    "PRO": 1000,
    "ENTERPRISE": -1,
}

@app.post("/api/v1/bot/request-access")
async def request_access(telegram_id: int, username: str):
    """Создаёт заявку на доступ (статус pending)"""
    user = next((u for u in users_db if u["telegram_id"] == telegram_id), None)
    if user and user["status"] == "active":
        return {"success": False, "message": "Доступ уже открыт"}
    if not user:
        users_db.append({
            "telegram_id": telegram_id,
            "username": username,
            "status": "pending",
            "subscription": "NONE",
            "requests_limit": 0,
            "requests_used": 0,
            "expires_at": "1970-01-01",
        })
    else:
        user["status"] = "pending"
        user["username"] = username
    return {"success": True, "message": "Заявка создана"}

@app.post("/api/v1/bot/approve-user")
async def approve_user(telegram_id: int, plan: str):
    """Админ одобряет доступ с выбранным тарифом"""
    from datetime import datetime, timedelta
    if plan not in PLANS:
        return {"success": False, "message": "Неизвестный тариф"}
    user = next((u for u in users_db if u["telegram_id"] == telegram_id), None)
    if not user:
        return {"success": False, "message": "Пользователь не найден"}
    user["status"] = "active"
    user["subscription"] = plan
    user["requests_limit"] = PLANS[plan]
    user["requests_used"] = 0
    user["expires_at"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    return {"success": True, "message": f"Тариф {plan} активирован", "expires_at": user["expires_at"]}   
