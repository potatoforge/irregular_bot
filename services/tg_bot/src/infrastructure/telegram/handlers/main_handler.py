import logging

from aiogram import F, Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.tg_bot.src.config.settings import settings
from services.tg_bot.src.container import Container
from services.tg_bot.src.domain.user import User
from services.tg_bot.src.infrastructure.telegram.keyboards.main_keyboard import (
    main_kr,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.tg_bot.src.domain.irregular_game import IrregularVerbGameScore
    from uuid import UUID

logger = logging.getLogger(__name__)

main_router = Router()

container = Container.build(settings=settings)
user_repository = container.user_repository
irregular_game_repository = container.irregular_game_repository


@main_router.message(F.text == "Hello")
@main_router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await set_user(
        tg_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    score = await get_user_score(user.id)
    await message.answer(
        f"Hello, {user.first_name if user.first_name else user.username}!",
        reply_markup=main_kr(),
    )
    await message.answer(f"Your current score: {html.bold(str(score.score))}")


async def set_user(
    tg_user_id: int, username: str | None, first_name: str | None, last_name: str | None
) -> User:
    user = await get_user(tg_user_id)
    if user is None:
        user = await user_repository.create_user(
            User(
                tg_id=tg_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        )
    return user


async def get_user(tg_user_id: int) -> User | None:
    user = await user_repository.get_user_by_tg_id(tg_user_id)
    if not user:
        return None
    return user


async def get_user_score(user_id: UUID) -> IrregularVerbGameScore:
    return await irregular_game_repository.get_user_score_by_id(user_id)
