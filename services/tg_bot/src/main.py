import asyncio
import logging
import logging.config
import sys
from os import getenv
from uuid import uuid4

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage

from services.tg_bot.src.config.settings import settings, LOGGING
from services.tg_bot.src.container import Container

from services.tg_bot.src.infrastructure.telegram.handlers.main_handler import (
    main_router,
)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("TG_BOT_KEY", "not-installed")
ADMIN_ID = int(getenv("ADMIN_ID", "0"))

# All handlers should be attached to the Router (or Dispatcher)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

container = Container.build(settings=settings)
user_repository = container.user_repository
verb_repository = container.verb_repository


async def set_commands(bot: Bot):
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


# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     """
#     This handler receives messages with `/start` command
#     """
#     # Most event objects have aliases for API methods that can be called in events' context
#     # For example if you want to answer to incoming message you can use `message.answer(...)` alias
#     # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
#     # method automatically or call API method directly via
#     # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`

#     user = await user_repository.get_user_by_tg_id(message.from_user.id)
#     if user is None:
#         await user_repository.create_user(
#             User(
#                 id=uuid4(),
#                 tg_id=message.from_user.id,
#                 username=message.from_user.username,
#                 first_name=message.from_user.first_name,
#                 last_name=message.from_user.last_name,
#             )
#         )

#     await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


# @dp.message()
# async def echo_handler(message: Message) -> None:

#     verb = await verb_repository.get_random_irregular_verb()

#     try:
#         # Send a copy of the received message
#         await message.reply(
#             f"Random irregular verb:\n"
#             f"Base form: {html.bold(verb.base_form)}\n"
#             f"Past simple: {html.bold(verb.past_simple)}\n"
#             f"Past participle: {html.bold(verb.past_participle)}\n"
#             f"Translation: {html.bold(verb.translation)}"
#         )
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")


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
    "Started with settings: %s",
    settings.model_dump_json(indent=4, exclude={"postgresql": {"password"}}),
)


if __name__ == "__main__":
    asyncio.run(main())
