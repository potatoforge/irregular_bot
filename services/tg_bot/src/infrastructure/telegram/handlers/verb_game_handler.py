import logging
from asyncio import sleep

from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from services.tg_bot.src.domain.user import User
from services.tg_bot.src.infrastructure.repositories.game_repository import (
    IrregularGameRepository,
)
from services.tg_bot.src.infrastructure.repositories.user_repository import (
    UserRepository,
)
from services.tg_bot.src.infrastructure.repositories.verb_repository import (
    VerbRepository,
)
from services.tg_bot.src.infrastructure.telegram.keyboards.main_keyboard import (
    i_dont_know_kr,
    main_kr,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.tg_bot.src.domain.verb import IrregularVerb

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)
verb_router = Router()


class VerbStates(StatesGroup):
    waiting_for_verb = State()
    work_on_mistakes = State()


async def get_user(user_repository: UserRepository, tg_user_id: int) -> User | None:
    return await user_repository.get_user_by_tg_id(tg_user_id)


async def get_verb_by_id(verb_repository: VerbRepository, verb_id: int) -> IrregularVerb:
    return await verb_repository.get_irregular_verb_by_id(verb_id)


async def check_verb(verb_repository: VerbRepository, verb_id: int, user_input: str) -> bool:
    verb = await get_verb_by_id(verb_repository, verb_id)
    if verb is None:
        return False

    user_verbs = [v.strip().lower() for v in user_input.split(" ")]
    if len(user_verbs) != 3:
        logger.info(
            "User input does not contain exactly 3 verbs.", extra={"user_input": user_input}
        )
        return False

    logger.info(
        "Checking verb against user input", extra={"verb_id": verb_id, "user_verbs": user_verbs}
    )

    def match_form(db_form: str, user_form: str) -> bool:
        if "/" in db_form:
            parts = [p.strip().lower() for p in db_form.split("/")]
            return user_form in parts
        return db_form.lower() == user_form

    if (
        verb.base_form.lower() == user_verbs[0]
        and match_form(verb.past_simple, user_verbs[1])
        and match_form(verb.past_participle, user_verbs[2])
    ):
        logger.info("User input matches verb. Correct!", extra={"verb_id": verb_id})
        return True

    logger.info("User input does not match verb. Incorrect.", extra={"verb_id": verb_id})
    return False


@verb_router.message(F.text == "Get random verb")
async def cmd_get_random_verb_handler(
    message: Message,
    state: FSMContext,
    user_repository: UserRepository,
    verb_repository: VerbRepository,
) -> None:
    await state.clear()
    random_verb = await verb_repository.get_random_irregular_verb()

    user = await get_user(user_repository, message.from_user.id)
    user_id = user.id if user else None  # Безопасное получение ID без type: ignore

    await message.answer(
        f"Random irregular verb:\n"
        f"Translation: {html.bold(random_verb.translation)}\n"
        f"Base form: {html.bold(html.spoiler(random_verb.base_form))}\n",
        reply_markup=i_dont_know_kr(),
    )

    logger.info("User with requested", extra={"user_id": user_id, "verb": random_verb})
    await state.set_state(VerbStates.waiting_for_verb)
    await state.update_data(verb_id=random_verb.id, user_id=user_id)


@verb_router.message(VerbStates.waiting_for_verb)
async def check_verb_handler(
    message: Message,
    state: FSMContext,
    verb_repository: VerbRepository,
    irregular_game_repository: IrregularGameRepository,
) -> None:
    user_state_data = await state.get_data()
    verb_id = user_state_data.get("verb_id")
    user_id = user_state_data.get("user_id")

    if verb_id is None:
        await message.reply("No verb to check. Please get a random verb first.")
        return

    user_input = message.text
    if not user_input:
        await message.reply("Please provide an answer.")
        return

    is_correct = await check_verb(verb_repository, verb_id, user_input)
    if is_correct:
        user_score = await irregular_game_repository.increment_user_score(user_id)
        await message.answer(
            f"Correct! 🎉\nYour current score: {html.bold(str(user_score.score))}",
            reply_markup=main_kr(),
        )
        await state.clear()
    else:
        verb = await get_verb_by_id(verb_repository, verb_id)
        if message.text.lower() != "i don't know":
            await message.reply("Incorrect. ❌")

        await sleep(0.3)
        await message.answer("Let's work on your mistakes! 💪\nWrite it correctly:")
        await message.answer(
            f"Random irregular verb:\n"
            f"Translation: {html.bold(verb.translation)}\n"
            f"Base form: {html.bold(verb.base_form)}\n"
            f"Past simple: {html.bold(verb.past_simple)}\n"
            f"Past participle: {html.bold(verb.past_participle)}",
        )
        await sleep(0.3)
        await state.clear()
        await state.set_state(VerbStates.work_on_mistakes)
        await state.update_data(verb_id=verb_id, user_id=user_id)


@verb_router.message(VerbStates.work_on_mistakes)
async def fix_mistakes_handler(
    message: Message,
    state: FSMContext,
    verb_repository: VerbRepository,
) -> None:
    user_state_data = await state.get_data()
    verb_id = user_state_data.get("verb_id")
    user_input = message.text

    if not user_input:
        await message.reply("Please provide an answer.")
        return

    is_correct = await check_verb(verb_repository, verb_id, user_input)
    if is_correct:
        await message.reply("Great! 🎉\nYou fixed your mistake!", reply_markup=main_kr())
        await state.clear()
    else:
        await message.reply(
            "Still incorrect. ❌\nTry again or get a new verb.", reply_markup=main_kr()
        )


@verb_router.message(F.text == "Show my score")
async def show_score_handler(
    message: Message,
    state: FSMContext,
    user_repository: UserRepository,
    irregular_game_repository: IrregularGameRepository,
) -> None:
    await state.clear()
    user = await get_user(user_repository, message.from_user.id)
    if not user:
        return

    user_score = await irregular_game_repository.get_user_score_by_id(user.id)
    await message.answer(
        f'Your score in "irregular verbs game": {html.bold(str(user_score.score))}',
        reply_markup=main_kr(),
    )
