from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

answer_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👍", callback_data="like"),
            InlineKeyboardButton(text="👎", callback_data="dislike"),
        ],
    ]
)
