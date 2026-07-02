from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Главное меню с AI-модулями."""
    kb = [
        [
            KeyboardButton(text="AI Чат"),
            KeyboardButton(text="Исследование рынка"),
        ],
        [
            KeyboardButton(text="Контент"),
            KeyboardButton(text="Воронки продаж"),
        ],
        [
            KeyboardButton(text="Мой профиль"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def main_menu_keyboard(is_linked: bool = True) -> ReplyKeyboardMarkup:
    """Алиас для совместимости со start.py"""
    return main_menu_kb()


def expired_menu_kb() -> ReplyKeyboardMarkup:
    """Меню для пользователя с истёкшим доступом."""
    kb = [
        [
            KeyboardButton(text="Ввести токен"),
        ],
        [
            KeyboardButton(text="Мой профиль"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def enter_token_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для ввода токена."""
    kb = [
        [
            KeyboardButton(text="Ввести токен"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def payment_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню оплаты — inline кнопки для выбора тарифа."""
    kb = [
        [InlineKeyboardButton(text="⭐ Старт — 1 490₽/мес", callback_data="pay_start")],
        [InlineKeyboardButton(text="🔥 Бизнес — 2 490₽/мес", callback_data="pay_business")],
        [InlineKeyboardButton(text="💎 Премиум — 4 990₽/мес", callback_data="pay_premium")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка 'Назад' — inline."""
    kb = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)