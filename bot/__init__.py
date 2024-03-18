from bot.ollama.api import model_is_installed
from bot.settings import OLLAMA_MODEL


async def main() -> None:
    from bot.bot import bot as aiogram_bot
    from bot.bot import dp
    from bot.routers import completion, start

    if not model_is_installed(OLLAMA_MODEL):
        print(f"[FATAL] Model {OLLAMA_MODEL} is not installed")
        exit(1)
    dp.include_routers(start.router, completion.router)
    print(f"[OLLAMA] Selected base model -> {OLLAMA_MODEL}")
    print("[BOT] Start polling...")
    await dp.start_polling(aiogram_bot)  # type: ignore
