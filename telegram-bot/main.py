import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("BACKEND_URL", "http://ai-business-os-backend:8000/api/v1")

if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в файле .env!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЯ ===
class UserStates(StatesGroup):
    waiting_token = State()
    chat_mode = State()
    funnel_mode = State()
    content_mode = State()
    research_mode = State()

# === КЛАВИАТУРЫ ===
def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 AI Чат"), KeyboardButton(text="📊 Воронки продаж")],
            [KeyboardButton(text="📝 Контент"), KeyboardButton(text="🔍 Исследование рынка")],
            [KeyboardButton(text="📈 Мой профиль"), KeyboardButton(text="🔄 Новый токен")],
        ],
        resize_keyboard=True
    )

def get_back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад в меню")]],
        resize_keyboard=True
    )

# === КОМАНДА /START ===
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/bot/check-user", params={"telegram_id": telegram_id})
            data = response.json()
            
            if data.get("authorized"):
                limit_text = f"{data['requests_used']}/{data['requests_limit']}" if data['requests_limit'] != -1 else f"{data['requests_used']}/∞"
                await message.answer(
                    f"👋 С возвращением, {data['username']}!\n\n"
                    f"📊 Ваш профиль:\n"
                    f"• Тариф: {data['subscription']}\n"
                    f"• Запросы: {limit_text}\n"
                    f"• Действует до: {data['expires_at']}\n\n"
                    f"Выберите модуль:",
                    reply_markup=get_main_menu()
                )
            else:
                await state.set_state(UserStates.waiting_token)
                await message.answer(
                    "🤖 Добро пожаловать в AI Business OS!\n\n"
                    "Для доступа введите ваш токен активации.\n\n"
                    "💰 Тарифы:\n"
                    "• BASIC — 990 BYN/мес (100 запросов)\n"
                    "• PRO — 2990 BYN/мес (1000 запросов)\n"
                    "• ENTERPRISE — 9900 BYN/мес (безлимит)"
                )
        except Exception as e:
            logger.error(f"Error checking user: {e}")
            await message.answer("⚠️ Ошибка соединения с сервером.")

# === ГЛАВНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ (ИСПРАВЛЕННАЯ СТРОКА ЗДЕСЬ!) ===
@dp.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    text = message.text.strip()
    current_state = await state.get_state()
    
    # 1. Возврат в меню
    if text == "⬅️ Назад в меню":
        await state.clear()
        await message.answer("Выберите модуль:", reply_markup=get_main_menu())
        return
    
    # 2. Если ждем токен
    if current_state == "UserStates:waiting_token":
        await process_token_activation(message, telegram_id, text, state)
        return
    
    # 3. Кнопки меню
    if text == "📈 Мой профиль":
        await show_profile(message, telegram_id)
        return
    
    if text == "🔄 Новый токен":
        await state.set_state(UserStates.waiting_token)
        await message.answer("📝 Введите новый токен активации:")
        return
    
    # 4. Активация режимов
    if text == "💬 AI Чат":
        await state.set_state(UserStates.chat_mode)
        await message.answer("💬 **Режим AI-чата активирован**\n\nЗадайте любой вопрос:", reply_markup=get_back_menu())
        return
    if text == "📊 Воронки продаж":
        await state.set_state(UserStates.funnel_mode)
        await message.answer("📊 **Режим воронок продаж**\n\nОпишите ваш продукт (например: *онлайн-курс по фитнесу*):", reply_markup=get_back_menu())
        return
    if text == "📝 Контент":
        await state.set_state(UserStates.content_mode)
        await message.answer("📝 **Режим генерации контента**\n\nОпишите тему для поста:", reply_markup=get_back_menu())
        return
    if text == "🔍 Исследование рынка":
        await state.set_state(UserStates.research_mode)
        await message.answer("🔍 **Режим исследования рынка**\n\nУкажите нишу для анализа:", reply_markup=get_back_menu())
        return
    
    # 5. Обработка AI-запросов в активных режимах
    if current_state in ["UserStates:chat_mode", "UserStates:funnel_mode", "UserStates:content_mode", "UserStates:research_mode"]:
        await process_ai_request(message, telegram_id, text, current_state, state)
        return
    
    # 6. По умолчанию
    await message.answer("Выберите модуль:", reply_markup=get_main_menu())

# === ФУНКЦИИ-ПОМОЩНИКИ ===
async def process_token_activation(message: Message, telegram_id: int, token: str, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/bot/activate-token", json={"telegram_id": telegram_id, "token": token, "username": username})
            data = response.json()
            if data.get("success"):
                await state.clear()
                await message.answer(f"✅ {data['message']}\n\nВыберите модуль:", reply_markup=get_main_menu())
            else:
                await message.answer(f"❌ {data['message']}")
        except Exception as e:
            logger.error(f"Error activating token: {e}")
            await message.answer("⚠️ Ошибка подключения к серверу.")

async def show_profile(message: Message, telegram_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/bot/check-user", params={"telegram_id": telegram_id})
            data = response.json()
            if data.get("authorized"):
                limit_text = f"{data['requests_used']}/{data['requests_limit']}" if data['requests_limit'] != -1 else f"{data['requests_used']}/∞"
                await message.answer(f"📊 Ваш профиль:\n👤 Имя: {data['username']}\n👑 Тариф: {data['subscription']}\n📈 Запросы: {limit_text}\n📅 Действует до: {data['expires_at']}")
            else:
                await message.answer("❌ Доступ не активирован. Введите /start")
        except Exception as e:
            logger.error(f"Error showing profile: {e}")

async def process_ai_request(message: Message, telegram_id: int, text: str, current_state: str, state: FSMContext):
    mode_map = {
        "UserStates:chat_mode": "chat",
        "UserStates:funnel_mode": "funnel",
        "UserStates:content_mode": "content",
        "UserStates:research_mode": "research",
    }
    mode = mode_map.get(current_state, "chat")
    
    thinking_msg = await message.answer("🤔 Думаю...")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Проверяем лимиты перед запросом
            check = await client.get(f"{API_URL}/bot/check-user", params={"telegram_id": telegram_id})
            if not check.json().get("authorized"):
                await state.clear()
                await thinking_msg.delete()
                await message.answer("❌ Лимит исчерпан или доступ закрыт. Введите /start", reply_markup=get_main_menu())
                return
            
            # 2. Отправляем запрос в AI
            ai_resp = await client.post(
                f"{API_URL}/ai/chat",
                json={"telegram_id": telegram_id, "message": text, "module": mode},
                timeout=60.0
            )
            ai_data = ai_resp.json()
            
            # 3. Увеличиваем счетчик
            await client.post(f"{API_URL}/bot/increment-requests", params={"telegram_id": telegram_id})
            
            await thinking_msg.delete()
            
            # 4. Отправляем ответ (с разбивкой на части, если длинный)
            response_text = ai_data.get("response", "Не удалось получить ответ.")
            if len(response_text) > 4000:
                for i in range(0, len(response_text), 4000):
                    await message.answer(response_text[i:i+4000], parse_mode="Markdown")
            else:
                await message.answer(response_text, parse_mode="Markdown")
                
        except httpx.TimeoutException:
            await thinking_msg.delete()
            await message.answer("⏱️ Превышено время ожидания. Попробуйте ещё раз.")
        except Exception as e:
            logger.error(f"AI Request Error: {e}")
            await thinking_msg.delete()
            await message.answer("⚠️ Ошибка при обработке запроса.")

# === ЗАПУСК ===
async def main():
    logger.info("🤖 Запуск бота AI Business OS...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())