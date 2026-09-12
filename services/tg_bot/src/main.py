import asyncio
import logging
import logging.config
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from services.tg_bot.src.config.settings import LOGGING, settings
from services.tg_bot.src.container import Container
from services.tg_bot.src.infrastructure.telegram.handlers.main_handler import (
    main_router,
)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


TOKEN = getenv("TG_BOT_KEY", "not-installed")
ADMIN_ID = int(getenv("ADMIN_ID", "0"))

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

container = Container.build(settings=settings)
user_repository = container.user_repository
verb_repository = container.verb_repository


async def set_commands(bot: Bot) -> None:
    commands = [BotCommand(command="start", description="Старт")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot() -> None:
    user = await user_repository.get_user_by_tg_id(ADMIN_ID)
    if user is None:
        return
    await bot.send_message(user.tg_id, "Bot started!")


async def stop_bot() -> None:
    user = await user_repository.get_user_by_tg_id(ADMIN_ID)
    if user is None:
        return
    await bot.send_message(user.tg_id, "Bot stopped!")


async def main() -> None:
    await set_commands(bot)

    dp.include_router(main_router)

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


logger.info(
    "Started with settings",
    extra={"settings": settings.model_dump(exclude={"postgresql": {"password"}})},
)


if __name__ == "__main__":
    asyncio.run(main())
