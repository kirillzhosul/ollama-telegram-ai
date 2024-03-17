import asyncio
import json

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from keyboards import answer_keyboard, base_keyboard
from model_api import model_api_chat, translate
from models import ChatData, ChatUserInformation, ResponseChunk, ResponseDoneChunk
from settings import BASE_LANGUAGE, START_USER_MESSAGE, SYSTEM_MESSAGE, TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

chats: dict[int, ChatData] = {}


def _reset_chat(user_id: int, user_information: ChatUserInformation) -> str:
    if user_id in chats:
        del chats[user_id]
    preferences: list[str] = []
    chats[user_id] = ChatData(
        messages=[{"role": "user", "content": SYSTEM_MESSAGE.format(preferences)}],
        preferences=[],
    )
    prompt = START_USER_MESSAGE.format(user_information.full_name)
    return prompt


@dp.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "Welcome, please write something to me!", reply_markup=base_keyboard
    )


@dp.message()
async def answer(message: Message) -> None:
    if not message.from_user or not message.text:
        return print("[ERROR]: Invalid message")

    user_id = message.from_user.id
    prompt = message.text

    if prompt == "debug":
        await message.answer(str(chats))
        return
    if prompt == "New chat" or user_id not in chats:
        prompt = _reset_chat(
            user_id,
            ChatUserInformation(full_name=message.from_user.full_name),
        )
        await message.answer("New chat created!", reply_markup=base_keyboard)
    else:
        prompt = await translate(prompt, BASE_LANGUAGE, "en")
    print(f"[{user_id}]: {prompt}")

    chat = chats[user_id]
    chats[user_id].messages.append({"role": "user", "content": prompt})

    msg = await message.answer("... thinking ...")

    r = model_api_chat(chat.messages, "llama2")

    assistant_content = ""
    previous_content = assistant_content
    for line in r.iter_lines():
        if not line:
            continue
        raw_data = json.loads(line.decode("utf-8"))
        if raw_data["done"]:
            data = ResponseDoneChunk.model_validate(raw_data)
            try:
                await msg.edit_text(
                    text=assistant_content
                )  # , reply_markup=answer_keyboard)

            except Exception as e:
                pass
            print(f"[{user_id}]: Finished, translate...")
            await msg.edit_text(
                await translate(assistant_content, "en", BASE_LANGUAGE),
                reply_markup=answer_keyboard,
            )
            print(f"[{user_id}]: Finished, imagine...")
            await message.answer("... thinking ...")
        else:
            data = ResponseChunk.model_validate(raw_data)
            assistant_content += data.message.content
            if assistant_content == previous_content:
                continue
            diff = len(assistant_content) - len(previous_content)
            previous_content = assistant_content
            if diff <= 10:
                continue
            try:
                await msg.edit_text(assistant_content)
            except Exception as e:
                print(f"[FATAL]: {e}")
                continue
    chat.messages.append({"role": "assistant", "content": assistant_content})


if __name__ == "__main__":
    print("Run bot")
    asyncio.run(dp.start_polling(bot))  # type: ignore
