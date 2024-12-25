from bot.ollama.api import validate_installation_with_configuration
from bot.settings import OLLAMA_MODEL


async def main() -> None:
    # Pre validate required model and overall ollama health.
    await validate_installation_with_configuration(OLLAMA_MODEL)

    from bot.bot import bot as aiogram_bot
    from bot.bot import dp
    from bot.routers import completion, start

    dp.include_routers(start.router, completion.router)
    print(f"[OLLAMA] Selected base model -> {OLLAMA_MODEL}")
    print("[BOT] Start polling...")
    await dp.start_polling(aiogram_bot)  # type: ignore
