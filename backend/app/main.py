import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, async_session
from app.models import Base
from app.api.v1 import api_router
from app.telegram.routes import set_session_factory as telegram_set_sf
from app.api.v1.ai import set_session_factory as ai_set_sf, set_groq_client
from app.api.v1.admin import set_session_factory as admin_set_sf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_groq():
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            client = Groq(api_key=api_key)
            set_groq_client(client)
            logger.info("Groq client initialized")
        else:
            logger.warning("GROQ_API_KEY not set")
    except ImportError:
        logger.warning("groq package not installed")
    except Exception as e:
        logger.error(f"Groq init error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sf = async_session
    telegram_set_sf(sf)
    ai_set_sf(sf)
    admin_set_sf(sf)

    init_groq()

    logger.info("AI Business OS Backend started!")
    yield
    logger.info("AI Business OS Backend shutting down...")


app = FastAPI(
    title="AI Business OS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Business OS", "version": "1.0.0"}