import os
import asyncio
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("BACKEND_URL", "http://ai-business-os-backend:8000/api/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "5236809587"))

if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в файле .env!")

PLAN_LIMITS = {"BASIC": 100, "PRO": 1000, "ENTERPRISE": -1}

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

def get_subscribe_keyboard() -> InlineKeyboardMarkup:
    """Кнопки при исчерпанном лимите (замени username поддержки на свой!)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="add_balance")],
        [InlineKeyboardButton(text="📋 Мои тарифы", callback_data="show_tariffs")],
        [InlineKeyboardButton(text="🆘 Поддержка", url="https://t.me/your_support_username")],
    ])

def get_request_access_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Запросить доступ", callback_data="request_access")]
    ])

def get_admin_approve_keyboard(tid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🥉 BASIC", callback_data=f"approve_{tid}_BASIC"),
         InlineKeyboardButton(text="🥈 PRO", callback_data=f"approve_{tid}_PRO")],
        [InlineKeyboardButton(text="🥇 ENTERPRISE", callback_data=f"approve_{tid}_ENTERPRISE"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{tid}")],
    ])

# === КОМАНДА /START ===
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id

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
                    "Для доступа оставьте заявку — администратор откроет его после оплаты.\n"
                    "Если у вас УЖЕ есть токен активации — просто введите его.\n\n"
                    "💰 Тарифы:\n"
                    "• BASIC — 990 BYN/мес (100 запросов)\n"
                    "• PRO — 2990 BYN/мес (1000 запросов)\n"
                    "• ENTERPRISE — 9900 BYN/мес (безлимит)",
                    reply_markup=get_request_access_keyboard()
                )
        except Exception as e:
            logger.error(f"Error checking user: {e}")
            await message.answer("⚠️ Ошибка соединения с сервером.")

# === ГЛАВНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ ===
@dp.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    text = message.text.strip()
    current_state = await state.get_state()

    if text == "⬅️ Назад в меню":
        await state.clear()
        await message.answer("Выберите модуль:", reply_markup=get_main_menu())
        return

    if current_state == "UserStates:waiting_token":
        await process_token_activation(message, telegram_id, text, state)
        return

    if text == "📈 Мой профиль":
        await show_profile(message, telegram_id)
        return

    if text == "🔄 Новый токен":
        await state.set_state(UserStates.waiting_token)
        await message.answer("📝 Введите новый токен активации:")
        return

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

    if current_state in ["UserStates:chat_mode", "UserStates:funnel_mode", "UserStates:content_mode", "UserStates:research_mode"]:
        await process_ai_request(message, telegram_id, text, current_state, state)
        return

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
                reason = data.get("message", "Доступ не активирован")
                await message.answer(
                    f"⚠️ <b>{reason}</b>\n\nДля доступа введите /start или приобретите подписку:",
                    parse_mode="HTML",
                    reply_markup=get_subscribe_keyboard()
                )
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
            check = await client.get(f"{API_URL}/bot/check-user", params={"telegram_id": telegram_id})
            check_data = check.json()

            if not check_data.get("authorized"):
                await state.clear()
                try:
                    await thinking_msg.delete()
                except Exception:
                    pass

                reason = check_data.get("message", "Доступ ограничен")
                reply_text = f"⚠️ <b>{reason}</b>\n\n"
                reply_text += "Чтобы продолжить работу с AI-аналитикой, оформите подписку или пополните баланс. "
                reply_text += "Это займёт всего 1 минуту! ⚡️\n\n"
                reply_text += "Выберите действие ниже 👇"

                await message.answer(reply_text, parse_mode="HTML", reply_markup=get_subscribe_keyboard())
                return

            ai_resp = await client.post(
                f"{API_URL}/ai/chat",
                json={"telegram_id": telegram_id, "message": text, "module": mode},
                timeout=60.0
            )
            ai_data = ai_resp.json()

            await client.post(f"{API_URL}/bot/increment-requests", params={"telegram_id": telegram_id})

            try:
                await thinking_msg.delete()
            except Exception:
                pass

            response_text = ai_data.get("response", "Не удалось получить ответ.")
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                try:
                    await message.answer(chunk, parse_mode="Markdown")
                except Exception:
                    await message.answer(chunk)

        except httpx.TimeoutException:
            try:
                await thinking_msg.delete()
            except Exception:
                pass
            await message.answer("⏱️ Превышено время ожидания. Попробуйте ещё раз.")
        except Exception as e:
            logger.error(f"AI Request Error: {e}")
            try:
                await thinking_msg.delete()
            except Exception:
                pass
            await message.answer("⚠️ Ошибка при обработке запроса.")

# === ОБРАБОТКА INLINE-КНОПОК ===
@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    data = callback.data
    tid = callback.from_user.id

    # Клиент запрашивает доступ
    if data == "request_access":
        username = callback.from_user.username or callback.from_user.full_name
        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/bot/request-access", params={"telegram_id": tid, "username": username})
        await callback.answer("Заявка отправлена!", show_alert=True)
        await callback.message.answer("✅ Заявка отправлена администратору. Как только доступ откроют — бот напишет вам!")
        # Уведомление админу НА ТЕЛЕФОН
        await bot.send_message(
            ADMIN_ID,
            f"🔔 <b>Новая заявка на доступ!</b>\n\n"
            f"👤 Клиент: {username}\n"
            f"🆔 ID: <code>{tid}</code>\n\n"
            f"Выбери тариф (после подтверждения оплаты):",
            parse_mode="HTML",
            reply_markup=get_admin_approve_keyboard(tid),
        )
        return

    # Админ одобряет заявку
    if data.startswith("approve_"):
        if tid != ADMIN_ID:
            await callback.answer("⛔ Только для администратора!", show_alert=True)
            return
        _, target_id, plan = data.split("_")
        target_id = int(target_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{API_URL}/bot/approve-user", params={"telegram_id": target_id, "plan": plan})
            result = resp.json()
        if result.get("success"):
            await callback.answer("Доступ открыт ✅")
            await callback.message.edit_text(f"✅ Заявка {target_id} одобрена: тариф {plan}")
            limit = PLAN_LIMITS[plan]
            await bot.send_message(
                target_id,
                f"🎉 <b>Доступ открыт!</b>\n\n"
                f"👑 Тариф: {plan}\n"
                f"📈 Запросов: {limit if limit != -1 else '∞'}\n"
                f"📅 Действует до: {result.get('expires_at')}\n\n"
                f"Нажми /start и приступай к работе!",
                parse_mode="HTML",
            )
        else:
            await callback.answer("Не удалось открыть доступ", show_alert=True)
        return

    # Админ отклоняет заявку
    if data.startswith("reject_"):
        if tid != ADMIN_ID:
            await callback.answer("⛔ Только для администратора!", show_alert=True)
            return
        target_id = int(data.split("_")[1])
        await callback.answer("Заявка отклонена")
        await callback.message.edit_text(f"❌ Заявка {target_id} отклонена")
        await bot.send_message(target_id, "😔 К сожалению, заявка отклонена. По вопросам оплаты напишите в поддержку.")
        return

    await callback.answer()

# === ЗАПУСК ===
async def main():
    logger.info("🤖 Запуск бота AI Business OS...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())