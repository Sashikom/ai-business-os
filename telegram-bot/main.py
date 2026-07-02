import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.chat import router as chat_router
from handlers.back import router as back_router
from handlers.payments import router as payments_router

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрируем обработчики
dp.include_router(admin_router)
dp.include_router(start_router)
dp.include_router(back_router)      # ← ПЕРЕД chat_router!
dp.include_router(chat_router)
dp.include_router(payments_router)


async def main():
    logging.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())