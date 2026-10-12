from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.filters import Command

from api_client import api_client

router = Router()

ADMIN_TELEGRAM_ID = 5236809587


def is_admin(telegram_id: int) -> bool:
    return telegram_id == ADMIN_TELEGRAM_ID


@router.message(Command("gen"))
async def cmd_gen(message: Message):
    """Команда /gen — генерация токенов (админ)."""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Эта команда только для администратора.")
        return

    # Парсим параметры: /gen [количество] [дней]
    parts = message.text.strip().split()
    count = 1
    days = 30

    if len(parts) >= 2:
        try:
            count = int(parts[1])
        except ValueError:
            await message.answer("Формат: /gen [количество] [дней]")
            return

    if len(parts) >= 3:
        try:
            days = int(parts[2])
        except ValueError:
            await message.answer("Формат: /gen [количество] [дней]")
            return

    result = await api_client.generate_tokens(
        admin_telegram_id=message.from_user.id,
        count=count,
        duration_days=days,
    )

    if not result:
        await message.answer("Ошибка генерации токенов.")
        return

    tokens = result.get("tokens", [])
    text = f"✅ Сгенерировано токенов: {len(tokens)} (на {days} дней)\n\n"
    for t in tokens:
        text += f"<code>{t}</code>\n"

    await message.answer(text)


@router.message(Command("tokens"))
async def cmd_tokens(message: Message):
    """Команда /tokens — список токенов (админ)."""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Эта команда только для администратора.")
        return

    result = await api_client.list_tokens(
        admin_telegram_id=message.from_user.id,
    )

    if not result:
        await message.answer("Ошибка получения списка токенов.")
        return

    tokens = result.get("tokens", [])
    if not tokens:
        await message.answer("Токенов пока нет. Используйте /gen для генерации.")
        return

    text = f"🎫 Всего токенов: {result.get('count', 0)}\n\n"
    for t in tokens[:20]:  # Показываем первые 20
        status = "ИСПОЛЬЗОВАН" if t.get("is_used") else "СВОБОДЕН"
        text += f"<code>{t.get('token')}</code> — {status}"
        if t.get("used_by"):
            text += f" (пользователь: {t.get('used_by')})"
        text += "\n"

    if len(tokens) > 20:
        text += f"\n... и ещё {len(tokens) - 20} токенов"

    await message.answer(text)


@router.message(Command("users"))
async def cmd_users(message: Message):
    """Команда /users — список пользователей (админ)."""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Эта команда только для администратора.")
        return

    result = await api_client.list_users(
        admin_telegram_id=message.from_user.id,
    )

    if not result:
        await message.answer("Ошибка получения списка пользователей.")
        return

    users = result.get("users", [])
    if not users:
        await message.answer("Пользователей пока нет.")
        return

    text = f"👥 Всего пользователей: {result.get('count', 0)}\n\n"
    for u in users[:20]:  # Показываем первые 20
        access = "ДА" if u.get("has_access") else "НЕТ"
        text += (
            f"@{u.get('username') or 'без_ника'} "
            f"({u.get('telegram_id')}) — "
            f"{u.get('subscription_status')} "
            f"доступ:{access} "
            f"дней:{u.get('days_left')}\n"
        )

    if len(users) > 20:
        text += f"\n... и ещё {len(users) - 20} пользователей"

    await message.answer(text)


@router.message(Command("block"))
async def cmd_block(message: Message):
    """Команда /block — заблокировать пользователя (админ)."""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Эта команда только для администратора.")
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("Формат: /block <telegram_id>")
        return

    try:
        block_id = int(parts[1])
    except ValueError:
        await message.answer("telegram_id должен быть числом")
        return

    result = await api_client.block_user(
        admin_telegram_id=message.from_user.id,
        block_telegram_id=block_id,
    )

    if not result:
        await message.answer("Ошибка блокировки пользователя.")
        return

    await message.answer(f"✅ Пользователь {block_id} заблокирован.")


@router.message(Command("panel"))
async def cmd_panel(message: Message):
    """Команда /panel — открыть веб-админку (React Web App)."""
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Эта команда только для администратора.")
        return

    # Ссылка на твою собранную админ-панель на Netlify
    web_app_url = "https://glistening-salamander-374aa6.netlify.app"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть Админ-панель", web_app=WebAppInfo(url=web_app_url))]
    ])

    await message.answer(
        "👨‍💼 <b>Веб-панель администратора AIBOS</b>\n\n"
        "Управляйте токенами, пользователями и смотрите статистику через удобный графический интерфейс.\n"
        "Нажмите кнопку ниже, чтобы открыть приложение 👇",
        reply_markup=keyboard
    )