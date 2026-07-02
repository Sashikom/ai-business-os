import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import main_menu_kb, main_menu_keyboard, expired_menu_kb
from api_client import APIClient

router = Router()
logger = logging.getLogger(__name__)

ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "5236809587")


class LinkStates(StatesGroup):
    waiting_for_email = State()


class TokenStates(StatesGroup):
    waiting_for_token = State()


# ВАЖНО: Обработчик "Назад" стоит ПЕРВЫМ!
@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message, state: FSMContext):
    """Возврат в главное меню."""
    await state.clear()
    api = APIClient()
    profile = await api.get_me(str(message.from_user.id))
    
    if profile:
        is_superuser = profile.get("is_superuser", False)
        has_access = profile.get("has_access", False)
        credits = profile.get("credits_balance", 0)
        days_left = profile.get("days_left", 0)
        
        if is_superuser:
            text = (
                f"<b>AI Business OS</b>\n\n"
                f"Режим: АДМИНИСТРАТОР\n"
                f"Кредиты: <b>{credits}</b>\n\n"
                f"Полный доступ без ограничений"
            )
        elif has_access:
            text = (
                f"<b>AI Business OS</b>\n\n"
                f"Режим: Активен ({days_left} дн.)\n"
                f"Кредиты: <b>{credits}</b>"
            )
        else:
            text = "<b>⚠️ Доступ ограничен</b>\n\nДля продления: /token"
        
        await message.answer(text, reply_markup=main_menu_keyboard(is_linked=True))
    else:
        await message.answer("Аккаунт не найден. Нажмите /start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    ref_code = None
    if message.text and message.text.startswith("/start ref_"):
        ref_code = message.text.replace("/start ref_", "")

    api = APIClient()
    profile = await api.get_me(str(message.from_user.id))

    if not profile:
        # Новый пользователь — просим токен
        text = (
            f"<b>👋 Добро пожаловать в AI Business OS!</b>\n\n"
            f"Для доступа к AI-модулям нужен токен активации.\n\n"
            f"💰 <b>Стоимость:</b> 990₽ за 30 дней\n"
            f"📧 <b>Связаться с админом:</b> @Sashikom\n\n"
            f"После оплаты вы получите токен вида:\n"
            f"<code>AIBOS-XXXXXXXX-XXXXXXXX</code>\n\n"
            f"Отправьте его командой:\n"
            f"/token ВАШ_ТОКЕН"
        )
        await message.answer(text)
        
        # Уведомляем админа
        try:
            ref_info = f"\nПригласил: ref_{ref_code}" if ref_code else ""
            await message.bot.send_message(
                int(ADMIN_TELEGRAM_ID),
                f"🆕 <b>Новый юзер!</b>\n\n"
                f"@{message.from_user.username or '?'} (ID: {message.from_user.id})\n"
                f"Имя: {message.from_user.full_name}{ref_info}\n\n"
                f"Нужно продать токен за 990₽"
            )
        except Exception:
            pass
    else:
        # Существующий пользователь
        is_superuser = profile.get("is_superuser", False)
        has_access = profile.get("has_access", False)
        days_left = profile.get("days_left", 0)
        sub = profile.get("subscription_status", "DEMO")
        credits = profile.get("credits_balance", 0)

        if is_superuser:
            text = (
                f"<b>AI Business OS</b>\n\n"
                f"Режим: АДМИНИСТРАТОР\n"
                f"Кредиты: <b>{credits}</b>\n\n"
                f"Полный доступ без ограничений"
            )
            await message.answer(text, reply_markup=main_menu_keyboard(is_linked=True))
        elif has_access:
            if sub == "DEMO":
                text = (
                    f"<b>AI Business OS</b>\n\n"
                    f"Режим: ДЕМО ({days_left} дн. осталось)\n"
                    f"Кредиты: <b>{credits}</b>\n\n"
                    f"Для продления: /token"
                )
            else:
                text = (
                    f"<b>AI Business OS</b>\n\n"
                    f"Режим: Активен ({days_left} дн. осталось)\n"
                    f"Кредиты: <b>{credits}</b>"
                )
            await message.answer(text, reply_markup=main_menu_keyboard(is_linked=True))
        else:
            # Доступ истёк — просим токен
            text = (
                f"<b>⚠️ Демо-период закончился!</b>\n\n"
                f"Для продолжения работы нужен токен.\n\n"
                f"💰 <b>Стоимость:</b> 990₽ за 30 дней\n"
                f"📧 <b>Связаться с админом:</b> @Sashikom\n\n"
                f"Отправьте токен командой:\n"
                f"/token ВАШ_ТОКЕН"
            )
            await message.answer(text)


@router.message(Command("token"))
async def cmd_token(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) >= 2:
        token = args[1].strip()
        await _activate_token(message, token)
    else:
        await state.set_state(TokenStates.waiting_for_token)
        await message.answer(
            "Отправьте токен доступа в формате:\n"
            "<code>AIBOS-XXXXXXXX-XXXXXXXX</code>\n\n"
            "Токен можно получить у администратора после оплаты."
        )


@router.message(TokenStates.waiting_for_token)
async def process_token(message: Message, state: FSMContext):
    token = message.text.strip()
    await _activate_token(message, token)
    await state.clear()


async def _activate_token(message: Message, token: str):
    api = APIClient()
    result = await api.activate_token(telegram_id=str(message.from_user.id), token=token)
    if "message" in result and "activated" in result.get("message", "").lower():
        days = result.get("days_left", 30)
        await message.answer(
            f"<b>Доступ активирован!</b>\n\n"
            f"Действителен: <b>{days} дней</b>\n"
            f"Теперь вы можете пользоваться всеми AI модулями!",
            reply_markup=main_menu_keyboard(is_linked=True)
        )
        try:
            await message.bot.send_message(
                int(ADMIN_TELEGRAM_ID),
                f"🔑 <b>Токен активирован!</b>\n\n"
                f"@{message.from_user.username or '?'} (ID: {message.from_user.id})"
            )
        except Exception:
            pass
    else:
        await message.answer(
            f"Ошибка активации: {result.get('detail', 'Неверный токен')}\n\n"
            "Проверьте токен и попробуйте снова: /token"
        )


@router.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Отправьте: /link ваш@email.com")
        return
    email = args[1].strip()
    api = APIClient()
    result = await api.request_link_code(email)
    if "code" in result:
        await state.set_state(LinkStates.waiting_for_email)
        await state.update_data(email=email, code=result["code"])
        await message.answer(f"Код привязки: <b>{result['code']}</b>\n\nНажмите кнопку для подтверждения:", reply_markup=back_keyboard("confirm_link"))
    else:
        await message.answer(f"Ошибка: {result.get('detail', 'Не удалось получить код')}")


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    api = APIClient()
    profile = await api.get_me(str(message.from_user.id))
    if not profile:
        await message.answer("Аккаунт не найден. Нажмите /start")
        return
    is_superuser = profile.get("is_superuser", False)
    sub = profile.get("subscription_status", "DEMO")
    days = profile.get("days_left", 0)
    has_access = profile.get("has_access", False)
    if is_superuser:
        status = "АДМИНИСТРАТОР"
    elif has_access:
        status = "Активен"
    else:
        status = "Истёк"
    await message.answer(
        f"<b>Ваш баланс</b>\n\n"
        f"Статус: {status}\n"
        f"Режим: {sub}\n"
        f"Дней осталось: {days}\n"
        f"Кредиты: {profile.get('credits_balance', 0)}\n"
        f"Использовано: {profile.get('credits_used', 0)}"
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    api = APIClient()
    profile = await api.get_me(str(callback.from_user.id))
    if profile:
        is_superuser = profile.get("is_superuser", False)
        has_access = profile.get("has_access", False)
        if is_superuser or has_access:
            days = profile.get("days_left", 0)
            sub = profile.get("subscription_status", "DEMO")
            if is_superuser:
                text = f"<b>AI Business OS - Главное меню</b>\n\nРежим: АДМИНИСТРАТОР\nКредиты: {profile.get('credits_balance', 0)}"
            else:
                text = f"<b>AI Business OS - Главное меню</b>\n\nРежим: {sub} ({days} дн.)\nКредиты: {profile.get('credits_balance', 0)}"
            await callback.message.edit_text(text, reply_markup=main_menu_keyboard(is_linked=True))
        else:
            text = "<b>Демо-период закончился!</b>\n\nДля оплаты нажмите кнопку ниже."
            await callback.message.edit_text(text, reply_markup=expired_keyboard())
    else:
        text = "Аккаунт не найден. Нажмите /start"
        await callback.message.edit_text(text, reply_markup=main_menu_keyboard(is_linked=False))


@router.callback_query(F.data == "confirm_link")
async def cb_confirm_link(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = data.get("code", "")
    if not code:
        await callback.message.edit_text("Код не найден. Начните заново: /link email")
        await state.clear()
        return
    api = APIClient()
    result = await api.confirm_link(telegram_id=str(callback.from_user.id), telegram_username=callback.from_user.username, telegram_name=callback.from_user.full_name, code=code)
    if "access_token" in result:
        await callback.message.edit_text("Аккаунт привязан!\n\nТеперь вы можете использовать AI модули!", reply_markup=main_menu_keyboard(is_linked=True))
    else:
        await callback.message.edit_text(f"Ошибка привязки: {result.get('detail', 'Неизвестная ошибка')}")
    await state.clear()


@router.callback_query(F.data == "my_balance")
async def cb_balance(callback: CallbackQuery):
    api = APIClient()
    profile = await api.get_me(str(callback.from_user.id))
    if not profile:
        await callback.message.edit_text("Аккаунт не найден", reply_markup=back_keyboard("main_menu"))
        return
    is_superuser = profile.get("is_superuser", False)
    sub = profile.get("subscription_status", "DEMO")
    days = profile.get("days_left", 0)
    has_access = profile.get("has_access", False)
    if is_superuser:
        status = "АДМИНИСТРАТОР"
    elif has_access:
        status = "Активен"
    else:
        status = "Истёк"
    await callback.message.edit_text(
        f"<b>Баланс</b>\n\nСтатус: {status}\nРежим: {sub}\nДней: {days}\nКредиты: {profile.get('credits_balance', 0)}\nИспользовано: {profile.get('credits_used', 0)}",
        reply_markup=back_keyboard("main_menu")
    )


@router.callback_query(F.data == "settings")
async def cb_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Настройки</b>\n\n"
        "/token - Активировать токен доступа\n"
        "/balance - Проверить баланс\n"
        "/link - Привязать email\n\n"
        "🎁 Пригласите друга и получите 100 кредитов!\n"
        "Ваша реферальная ссылка:\n"
        f"<code>https://t.me/Sashikom_bot?start=ref_{callback.from_user.id}</code>",
        reply_markup=back_keyboard("main_menu")
    )