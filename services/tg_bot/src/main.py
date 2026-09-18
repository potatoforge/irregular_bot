import asyncio
import logging
import logging.config
from os import getenv
from collections.abc import AsyncGenerator

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from contextlib import asynccontextmanager
from services.tg_bot.src.config.settings import LOGGING, settings
from services.tg_bot.src.container import Container
from services.tg_bot.src.infrastructure.telegram.handlers.main_handler import (
    main_router,
)
from services.tg_bot.src.infrastructure.telegram.handlers.verb_game_handler import (
    verb_router,
)
from services.tg_bot.src.infrastructure.repositories.user_repository import (
    UserRepository,
)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


TOKEN = getenv("TG_BOT_KEY", "not-installed")
ADMIN_ID = int(getenv("ADMIN_ID", "0"))


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(
    storage=MemoryStorage(),
)


async def set_commands(bot: Bot) -> None:
    commands = [BotCommand(command="start", description="Старт")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def send_start_status(user_repository: UserRepository) -> None:
    user = await user_repository.get_user_by_tg_id(ADMIN_ID)
    if user is None:
        return
    await bot.send_message(user.tg_id, "Bot started!")


async def send_stop_status(user_repository: UserRepository) -> None:
    user = await user_repository.get_user_by_tg_id(ADMIN_ID)
    if user is None:
        return
    await bot.send_message(user.tg_id, "Bot stopped!")


@asynccontextmanager
async def lifespan(dispatcher: Dispatcher, bot_instance: Bot) -> AsyncGenerator[None]:
    container = Container.build(settings=settings)

    await container.pg_connector.connect()

    await set_commands(bot)
    await bot_instance.delete_webhook(drop_pending_updates=True)

    dispatcher["user_repository"] = container.user_repository
    dispatcher["verb_repository"] = container.verb_repository
    dispatcher["irregular_game_repository"] = container.irregular_game_repository

    dispatcher.include_router(main_router)
    dispatcher.include_router(verb_router)

    await send_start_status(container.user_repository)

    yield

    await send_stop_status(container.user_repository)
    await container.pg_connector.disconnect()
    await bot_instance.session.close()


async def main() -> None:

    async with lifespan(dp, bot):
        await dp.start_polling(bot)


logger.info(
    "Started with settings",
    extra={"settings": settings.model_dump(exclude={"postgresql": {"password"}})},
)


if __name__ == "__main__":
    asyncio.run(main())
