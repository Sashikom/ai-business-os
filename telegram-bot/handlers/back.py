from aiogram import Router, F
from aiogram.types import Message
from keyboards import main_menu_kb

router = Router()


@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message):
    """Возврат в главное меню."""
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_kb()
    )