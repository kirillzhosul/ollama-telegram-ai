from aiogram import Router
from aiogram.filters.command import CommandStart
from aiogram.types import Message

from bot.keyboards.reply import base_keyboard

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(
        "Welcome, please write something to me! (/translate_on, /translate_off, /models, /model_set)",
        reply_markup=base_keyboard,
    )
