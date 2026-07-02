from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Generation, SubscriptionStatus

router = APIRouter(tags=["ai"])

_session_factory = None
_groq_client = None


def set_session_factory(sf):
    global _session_factory
    _session_factory = sf


def set_groq_client(client):
    global _groq_client
    _groq_client = client


def get_session():
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized")
    return _session_factory()


async def _check_access(telegram_id):
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.has_access:
            raise HTTPException(status_code=403, detail="Access expired")
        return user


class ChatRequest(BaseModel):
    telegram_id: int
    message: str
    module: str = "chat"


class ChatResponse(BaseModel):
    response: str
    module: str


SYSTEM_PROMPTS = {
    "chat": "You are a business AI assistant. Reply in Russian with practical advice.",
    "market_research": "You are a market research expert. Reply in Russian with structured analysis.",
    "content": "You are a content creation expert. Reply in Russian with ready-to-use texts.",
    "funnel": "You are a sales funnel expert. Reply in Russian with concrete schemes and texts.",
}


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest):
    user = await _check_access(req.telegram_id)

    if _groq_client is None:
        raise HTTPException(status_code=500, detail="Groq client not configured")

    system_prompt = SYSTEM_PROMPTS.get(req.module, SYSTEM_PROMPTS["chat"])

    try:
        completion = _groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    async with get_session() as session:
        generation = Generation(
            user_id=user.id,
            module=req.module,
            prompt=req.message,
            result=response_text,
        )
        session.add(generation)
        await session.commit()

    return ChatResponse(response=response_text, module=req.module)