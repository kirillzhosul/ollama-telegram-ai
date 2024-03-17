from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

base_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="New chat")]],
    resize_keyboard=True,
    one_time_keyboard=False,
)
answer_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👍", callback_data="like"),
            InlineKeyboardButton(text="👎", callback_data="dislike"),
        ],
    ]
)
