import logging

from aiogram import F, Router, html
from aiogram.types import Message

from services.tg_bot.src.application.phrases.idioms_service import IdiomsService


logger = logging.getLogger(__name__)

phrase_router = Router()


@phrase_router.message(F.text == "Get new phrase")
async def get_phrase(message: Message, idiom_service: IdiomsService) -> None:
    logger.info("User requested a new phrase.", extra={"user_id": message.from_user.id})

    idiom = await idiom_service.get_idiom()

    await message.answer(
        f"{html.bold('Idiom:')} {html.italic(html.bold(idiom.idiom))}\n\n"
        f"{html.bold('Translation:')} {html.italic(idiom.translation)}\n\n"
        f"{html.bold('Meaning:')} {html.italic(idiom.meaning)}\n\n"
        f"{html.bold('Usage context:')} {idiom.context}\n\n"
        f"{html.bold('Source:')} {html.link('link to source', idiom.source)}"
    )
