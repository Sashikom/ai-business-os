import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import payment_menu_keyboard, back_keyboard
from api_client import APIClient

router = Router()
logger = logging.getLogger(__name__)

ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "5236809587")

PAYMENT_CARD = 9112501074516249  # Замени на свой номер карты
PAYMENT_NAME = "Alexander M."  # Замени на имя владельца карты

TARIFFS = {
    "start": {"name": "СТАРТ", "price": 990, "stars": 150, "credits": 2000, "days": 30},
    "business": {"name": "БИЗНЕС", "price": 2990, "stars": 450, "credits": 5000, "days": 30},
    "premium": {"name": "ПРЕМИУМ", "price": 5990, "stars": 900, "credits": 99999, "days": 365},
}

EXTRA_CREDITS = {
    "500": {"name": "500 кредитов", "stars": 75},
    "2000": {"name": "2000 кредитов", "stars": 250},
    "5000": {"name": "5000 кредитов", "stars": 550},
}


class PaymentStates(StatesGroup):
    waiting_payment_confirm = State()


# ===== МЕНЮ ОПЛАТЫ =====
@router.callback_query(F.data.startswith("pay_info_"))
async def cb_pay_info(callback: CallbackQuery):
    tariff_key = callback.data.replace("pay_info_", "")
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return
    text = (
        f"<b>{tariff['name']}</b>\n\n"
        f"💰 Цена: {tariff['price']} руб ({tariff['stars']} Stars)\n"
        f"📊 Кредиты: {tariff['credits']}\n"
        f"📅 Дней: {tariff['days']}\n\n"
        f"Выберите способ оплаты:"
    )
    from keyboards import tariff_keyboard
    await callback.message.edit_text(text, reply_markup=tariff_keyboard(tariff_key))
@router.callback_query(F.data == "pay_menu")
async def cb_pay_menu(callback: CallbackQuery):
    text = (
        f"<b>💳 Оплата подписки</b>\n\n"
        f"Выберите тариф:\n\n"
        f"🟡 СТАРТ — 990 руб (150 Stars)\n"
        f"   2000 кредитов, 30 дней\n\n"
        f"🔵 БИЗНЕС — 2990 руб (450 Stars)\n"
        f"   5000 кредитов, 30 дней\n\n"
        f"🟣 ПРЕМИУМ — 5990 руб (900 Stars)\n"
        f"   Безлимит, 365 дней"
    )
    await callback.message.edit_text(text, reply_markup=payment_menu_keyboard())


# ===== TELEGRAM STARS ОПЛАТА =====

@router.callback_query(F.data.startswith("pay_stars_"))
async def cb_pay_stars(callback: CallbackQuery):
    tariff_key = callback.data.replace("pay_stars_", "")
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return
    await callback.message.answer_invoice(
        title=f"AIBOS {tariff['name']}",
        description=f"Подписка {tariff['name']}: {tariff['credits']} кредитов, {tariff['days']} дней",
        payload=f"aibos_{tariff_key}",
        currency="XTR",
        prices=[LabeledPrice(label=f"AIBOS {tariff['name']}", amount=tariff["stars"])],
        provider_token="",
    )


@router.callback_query(F.data.startswith("pay_credits_stars_"))
async def cb_pay_credits_stars(callback: CallbackQuery):
    key = callback.data.replace("pay_credits_stars_", "")
    extra = EXTRA_CREDITS.get(key)
    if not extra:
        await callback.answer("Не найдено", show_alert=True)
        return
    await callback.message.answer_invoice(
        title=f"AIBOS {extra['name']}",
        description=f"Дополнительные кредиты: {extra['name']}",
        payload=f"aibos_credits_{key}",
        currency="XTR",
        prices=[LabeledPrice(label=extra["name"], amount=extra["stars"])],
        provider_token="",
    )


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    telegram_id = str(message.from_user.id)

    if payload.startswith("aibos_credits_"):
        key = payload.replace("aibos_credits_", "")
        extra = EXTRA_CREDITS.get(key, {})
        credits = int(key)
        api = APIClient()
        profile = await api.get_profile(telegram_id)
        if profile:
            m_result = await api.get_admin_users()
            for u in m_result.get("users", []):
                if str(u.get("telegram_id")) == telegram_id:
                    await api.add_credits(u.get("id", ""), credits)
                    break
        await message.answer(
            f"<b>✅ Оплата прошла!</b>\n\n"
            f"Начислено кредитов: {credits}\n"
            f"Спасибо за покупку!"
        )
        return

    tariff_key = payload.replace("aibos_", "")
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        await message.answer("✅ Оплата прошла! Свяжитесь с админом для активации.")
        return

    api = APIClient()
    profile = await api.get_profile(telegram_id)

    if not profile:
        await message.answer("✅ Оплата прошла! Нажмите /start для активации.")
        return

    m_result = await api.get_admin_users()
    for u in m_result.get("users", []):
        if str(u.get("telegram_id")) == telegram_id:
            await api.add_credits(u.get("id", ""), tariff["credits"])
            await api.change_subscription(u.get("id", ""), tariff_key.upper())
            break

    await message.answer(
        f"<b>✅ Подписка активирована!</b>\n\n"
        f"Тариф: {tariff['name']}\n"
        f"Кредиты: {tariff['credits']}\n"
        f"Дней: {tariff['days']}\n\n"
        f"Приятного использования! 🎉"
    )

    try:
        await message.bot.send_message(
            int(ADMIN_TELEGRAM_ID),
            f"💰 <b>Новая оплата!</b>\n\n"
            f"Юзер: @{message.from_user.username or telegram_id}\n"
            f"Тариф: {tariff['name']}\n"
            f"Stars: {tariff['stars']}"
        )
    except Exception:
        pass


# ===== РУЧНАЯ ОПЛАТА (КАРТА) =====

@router.callback_query(F.data.startswith("pay_card_"))
async def cb_pay_card(callback: CallbackQuery, state: FSMContext):
    tariff_key = callback.data.replace("pay_card_", "")
    tariff = TARIFFS.get(tariff_key)
    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return
    text = (
        f"<b>🏦 Перевод на карту</b>\n\n"
        f"Тариф: {tariff['name']} — {tariff['price']} руб\n\n"
        f"Реквизиты:\n"
        f"💳 Карта: <code>{PAYMENT_CARD}</code>\n"
        f"👤 Получатель: {PAYMENT_NAME}\n\n"
        f"1. Переведите {tariff['price']} руб на карту\n"
        f"2. Нажмите кнопку '✅ Я оплатил' ниже\n"
        f"3. Админ проверит и активирует подписку\n\n"
        f"⏱ Активация: от 5 минут до 2 часов"
    )
    await state.set_state(PaymentStates.waiting_payment_confirm)
    await state.update_data(tariff_key=tariff_key, tariff_name=tariff["name"])
    await callback.message.edit_text(
        text,
        reply_markup=back_keyboard("pay_menu")
    )
    await callback.message.answer(
        "Подтвердите оплату:",
        reply_markup=back_keyboard("pay_confirm")
    )


@router.callback_query(F.data == "pay_confirm")
async def cb_pay_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tariff_name = data.get("tariff_name", "?")
    tariff_key = data.get("tariff_key", "")
    await state.clear()

    text = (
        f"✅ <b>Заявка на активацию отправлена!</b>\n\n"
        f"Тариф: {tariff_name}\n\n"
        f"Админ проверит оплату и активирует подписку.\n"
        f"Обычно это занимает 5-30 минут."
    )
    await callback.message.edit_text(text)

    try:
        await callback.bot.send_message(
            int(ADMIN_TELEGRAM_ID),
            f"🏦 <b>Запрос на активацию!</b>\n\n"
            f"Юзер: @{callback.from_user.username or callback.from_user.id}\n"
            f"Telegram ID: {callback.from_user.id}\n"
            f"Тариф: {tariff_name}\n\n"
            f"Проверьте оплату и активируйте через админ-панель."
        )
    except Exception:
        pass


# ===== ДОПОЛНИТЕЛЬНЫЕ КРЕДИТЫ =====

@router.callback_query(F.data == "pay_extra_credits")
async def cb_extra_credits(callback: CallbackQuery):
    text = (
        f"<b>💰 Дополнительные кредиты</b>\n\n"
        f"500 кредитов — 75 Stars\n"
        f"2000 кредитов — 250 Stars\n"
        f"5000 кредитов — 550 Stars"
    )
    from keyboards import extra_credits_keyboard
    await callback.message.edit_text(text, reply_markup=extra_credits_keyboard())