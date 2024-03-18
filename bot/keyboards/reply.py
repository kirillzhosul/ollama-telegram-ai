from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

base_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="New chat")]],
    resize_keyboard=True,
    one_time_keyboard=False,
)
