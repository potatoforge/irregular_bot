import logging

from aiogram import F, Router
from aiogram.types import Message

from services.tg_bot.src.presentation.telegram.keyboards.main_keyboard import (
    main_kr,
)

logger = logging.getLogger(__name__)

phrase_router = Router()


@phrase_router.message(F.text == "Get new phrase")
async def get_phrase(message: Message) -> None:
    logger.info("User requested a new phrase.", extra={"user_id": message.from_user.id})
    await message.answer(
        "Here is your new phrase: 'The quick brown fox jumps over the lazy dog.'",
        reply_markup=main_kr(),
    )
