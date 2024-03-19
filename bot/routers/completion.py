from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from pydantic import BaseModel

from bot.bot import bot as aiogram_bot
from bot.keyboards.inline import answer_keyboard
from bot.keyboards.reply import base_keyboard
from bot.ollama import OllamaChat, OllamaChatMessage, generate_chat_completion
from bot.ollama.api import get_installed_models, model_is_installed
from bot.ollama.dto import OllamaErrorChunk
from bot.settings import (
    BASE_LANGUAGE,
    OLLAMA_MODEL,
    OLLAMA_MODEL_TEMPERATURE,
    START_USER_MESSAGE,
    SYSTEM_MESSAGE,
)
from bot.translator import translate

router = Router()


def wrap(s: str, w: int) -> list[str]:
    return [s[i : i + w] for i in range(0, len(s), w)]


class UserChat(BaseModel):
    ollama_chat: OllamaChat
    selected_model: str = OLLAMA_MODEL
    linked_last_messages: int | None = None
    do_translate: bool = True
    previous_prompt: str | None = None


chats: dict[int, UserChat] = {}


async def generate(message: Message, user_id: int, text: str):
    if text == "New chat":
        await message.answer("New chat created!", reply_markup=base_keyboard)
        return _delete_chat(user_id)
    if text == "/models":
        await message.answer(
            "\n".join([model.name for model in await get_installed_models()])
        )
        return
    if _create_chat(user_id):
        await message.answer(f"Chat created, model selected to {OLLAMA_MODEL}")
    chat = chats[user_id]

    if text == "/translate_on":
        chats[user_id].do_translate = True
        return
    if text == "/translate_off":
        chats[user_id].do_translate = False
        return
    try:
        if chat.linked_last_messages:
            await aiogram_bot.edit_message_reply_markup(
                user_id,
                message_id=chat.linked_last_messages,
                reply_markup=None,
            )
    except Exception:
        print("error on clear")

    chat.linked_last_messages = None

    if text.startswith("/set_model"):
        model_to_set = "".join(text.split()[1:])
        if not await model_is_installed(model_to_set):
            await message.answer(f"Model {model_to_set} does not exists!")
            return
        await message.answer(f"Model was set to {model_to_set}!")
        chats[user_id].selected_model = model_to_set

        return
    msg = await message.answer("... thinking ...")

    if chat.do_translate:
        prompt = await translate(text, BASE_LANGUAGE, "en")
    else:
        prompt = text
    chat.previous_prompt = prompt
    chat.ollama_chat.messages.append(OllamaChatMessage(role="user", content=prompt))
    print(f"[{user_id}]: {prompt}")

    assistant_content = ""
    async for is_done, chunk in generate_chat_completion(
        chat.ollama_chat.messages,
        OLLAMA_MODEL,
        temperature=OLLAMA_MODEL_TEMPERATURE,
    ):
        if is_done:
            wrapped_response = wrap(assistant_content, 4096)
            initial_content = wrapped_response.pop(0)
            try:
                await msg.edit_text(
                    (
                        (await translate(initial_content, "en", BASE_LANGUAGE))
                        if chat.do_translate
                        else initial_content
                    ),
                    reply_markup=None if wrapped_response else answer_keyboard,
                )
            except Exception:
                print("Error to set")
            if wrapped_response:
                for text in wrapped_response:
                    msg = await msg.answer(text)
                    if chat.do_translate:
                        await msg.edit_text(
                            (
                                (await translate(text, "en", BASE_LANGUAGE))
                                if chat.do_translate
                                else text
                            ),
                            reply_markup=answer_keyboard,
                        )
            print(f"[{user_id}]: Finished!")
        else:
            if isinstance(chunk, OllamaErrorChunk):
                await message.answer(f"error: {chunk.error}")
                break
            assistant_content += chunk.message.content
    chat.linked_last_messages = msg.message_id

    chat.ollama_chat.messages.append(
        OllamaChatMessage(role="assistant", content=assistant_content)
    )


def _delete_chat(user_id: int) -> None:
    if user_id not in chats:
        return
    del chats[user_id]


def _create_chat(user_id: int) -> bool:
    if user_id in chats:
        return False

    chats[user_id] = UserChat(
        selected_model=OLLAMA_MODEL,
        ollama_chat=OllamaChat(messages=[]),
    )
    if SYSTEM_MESSAGE:
        chats[user_id].ollama_chat.messages.append(
            OllamaChatMessage(role="system", content=SYSTEM_MESSAGE)
        )
    if START_USER_MESSAGE:
        chats[user_id].ollama_chat.messages.append(
            OllamaChatMessage(role="user", content=START_USER_MESSAGE)
        )
    return True


@router.callback_query(F.data == "like")
async def like(callback: CallbackQuery):
    if not callback.from_user:
        return print("[ERROR]: Invalid message")

    user_id = callback.from_user.id
    if user_id not in chats:
        return

    chat = chats[user_id]
    if chat.linked_last_messages:
        await aiogram_bot.edit_message_reply_markup(
            user_id,
            message_id=chat.linked_last_messages,
            reply_markup=None,
        )
    chat.linked_last_messages = None


@router.callback_query(F.data == "dislike")
async def dislike(callback: CallbackQuery):
    if not callback.from_user:
        return print("[ERROR]: Invalid message")

    user_id = callback.from_user.id
    if user_id not in chats:
        return

    chat = chats[user_id]
    if not chat.linked_last_messages:
        return
    await aiogram_bot.delete_message(
        user_id,
        message_id=chat.linked_last_messages,
    )
    if not chat.previous_prompt:
        return
    if not isinstance(callback.message, Message):
        raise Exception

    await generate(callback.message, user_id, chat.previous_prompt)


@router.message()
async def answer(message: Message) -> None:
    if message.from_user is None or message.text is None:
        return
    await generate(message, message.from_user.id, message.text)
