import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from api_client import api_client
from keyboards import main_menu_kb, expired_menu_kb

router = Router()

# Маппинг: пользователь -> выбранный модуль
_user_modules = {}


@router.message(Command("chat"))
async def cmd_chat(message: Message):
    """Команда /chat — включить режим AI чата."""
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result or not result.get("has_access"):
        await message.answer(
            "Доступ истёк! Активируйте токен командой /token",
            reply_markup=expired_menu_kb(),
        )
        return

    _user_modules[message.from_user.id] = "chat"
    await message.answer(
        "Режим AI Чат включён!\n\n"
        "Пишите любые вопросы — AI поможет.\n"
        "Для смены модуля нажмите нужную кнопку.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "AI Чат")
async def btn_ai_chat(message: Message):
    """Кнопка 'AI Чат'."""
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result or not result.get("has_access"):
        await message.answer(
            "Доступ истёк! Активируйте токен командой /token",
            reply_markup=expired_menu_kb(),
        )
        return

    _user_modules[message.from_user.id] = "chat"
    await message.answer(
        "Режим AI Чат включён!\n\n"
        "Пишите любые вопросы — AI поможет.",
    )


@router.message(F.text == "Исследование рынка")
async def btn_market(message: Message):
    """Кнопка 'Исследование рынка'."""
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result or not result.get("has_access"):
        await message.answer(
            "Доступ истёк! Активируйте токен командой /token",
            reply_markup=expired_menu_kb(),
        )
        return

    _user_modules[message.from_user.id] = "market_research"
    await message.answer(
        "Режим 'Исследование рынка' включён!\n\n"
        "Опишите нишу или рынок для анализа.\n"
        "Например: 'Проанализируй рынок онлайн-курсов по дизайну'",
    )


@router.message(F.text == "Контент")
async def btn_content(message: Message):
    """Кнопка 'Контент'."""
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result or not result.get("has_access"):
        await message.answer(
            "Доступ истёк! Активируйте токен командой /token",
            reply_markup=expired_menu_kb(),
        )
        return

    _user_modules[message.from_user.id] = "content"
    await message.answer(
        "Режим 'Контент' включён!\n\n"
        "Опишите, какой контент нужен.\n"
        "Например: 'Напиши пост для Instagram про новый продукт'",
    )


@router.message(F.text == "Воронки продаж")
async def btn_funnel(message: Message):
    """Кнопка 'Воронки продаж'."""
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result or not result.get("has_access"):
        await message.answer(
            "Доступ истёк! Активируйте токен командой /token",
            reply_markup=expired_menu_kb(),
        )
        return

    _user_modules[message.from_user.id] = "funnel"
    await message.answer(
        "Режим 'Воронки продаж' включён!\n\n"
        "Опишите ваш продукт и целевую аудиторию.\n"
        "Например: 'Сделай воронку продаж для онлайн-курса по фитнесу'",
    )


@router.message(F.text == "Мой профиль")
async def btn_profile(message: Message):
    """Кнопка 'Мой профиль'."""
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result:
        await message.answer("Ошибка получения профиля.")
        return

    status = result.get("subscription_status", "UNKNOWN")
    has_access = result.get("has_access", False)
    days_left = result.get("days_left", 0)

    status_text = {
        "DEMO": "Демо-доступ",
        "ACTIVE": "Полный доступ",
        "EXPIRED": "Истёк",
    }.get(status, status)

    text = (
        f"<b>Ваш профиль</b>\n\n"
        f"Статус: {status_text}\n"
        f"Доступ: {'Открыт' if has_access else 'Закрыт'}\n"
        f"Осталось дней: {days_left}\n"
    )

    if not has_access:
        await message.answer(text, reply_markup=expired_menu_kb())
    else:
        await message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == "Ввести токен")
async def btn_enter_token(message: Message):
    """Кнопка 'Ввести токен'."""
    await message.answer(
        "Введите токен доступа в формате:\n"
        "<code>AIBOS-XXXXXXXX-XXXXXXXX</code>",
    )


# Обработка обычных текстовых сообщений — отправляем в AI
@router.message(F.text)
async def handle_text(message: Message):
    """Обработка текстовых сообщений — отправка в AI."""
    # Проверяем доступ
    result = await api_client.get_me(telegram_id=message.from_user.id)
    if not result or not result.get("has_access"):
        await message.answer(
            "Доступ истёк! Активируйте токен командой /token",
            reply_markup=expired_menu_kb(),
        )
        return

    # Определяем модуль (по умолчанию chat)
    module = _user_modules.get(message.from_user.id, "chat")

    # Отправляем в AI
    await message.answer("Думаю...")

    ai_result = await api_client.ai_chat(
        telegram_id=message.from_user.id,
        message=message.text,
        module=module,
    )

    if not ai_result:
        await message.answer("Ошибка AI. Попробуйте позже.")
        return

    response = ai_result.get("response", "Нет ответа")
    await message.answer(response)
