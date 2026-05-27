import logging
from uuid import UUID
from asyncio import sleep
from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.tg_bot.src.infrastructure.telegram.keyboards.main_keyboard import (
    main_kr,
    i_dont_know_kr,
)
from services.tg_bot.src.container import Container
from services.tg_bot.src.config.settings import settings
from services.tg_bot.src.domain.user import User
from services.tg_bot.src.domain.verb import IrregularVerb
from services.tg_bot.src.domain.irregular_game import IrregularVerbGameScore

logger = logging.getLogger(__name__)

main_router = Router()

container = Container.build(settings=settings)
user_repository = container.user_repository
verb_repository = container.verb_repository
irregular_game_repository = container.irregular_game_repository


class VerbStates(StatesGroup):
    waiting_for_verb = State()
    work_on_mistakes = State()


@main_router.message(F.text == "Hello")
@main_router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext):
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


@main_router.message(F.text == "Get random verb")
async def cmd_get_random_verb_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    random_verb = await get_random_verb()
    user_id = (await get_user(tg_user_id=message.from_user.id)).id
    await message.answer(
        f"Random irregular verb:\n"
        f"Translation: {html.bold(random_verb.translation)}\n"
        f"Base form: {html.bold(html.spoiler(random_verb.base_form))}\n",
        reply_markup=i_dont_know_kr(),
    )

    logger.info(f"User with id={user_id} requested a random verb: {random_verb}")
    await state.set_state(VerbStates.waiting_for_verb)
    await state.update_data(verb_id=random_verb.id, user_id=user_id)


@main_router.message(VerbStates.waiting_for_verb)
async def check_verb_handler(message: Message, state: FSMContext) -> None:
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
    is_correct = await check_verb(verb_id, user_input)
    if is_correct:
        user_score = await irregular_game_repository.increment_user_score(user_id)
        await message.answer(
            f"Correct! 🎉\n" f"Your current score: {html.bold(str(user_score.score))}",
            reply_markup=main_kr(),
        )
        await state.clear()
    else:
        verb = await get_verb_by_id(verb_id)
        if not message.text.lower() == "i don't know":
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


@main_router.message(VerbStates.work_on_mistakes)
async def fix_mistakes_handler(message: Message, state: FSMContext):
    user_state_data = await state.get_data()
    verb_id = user_state_data.get("verb_id")
    user_id = user_state_data.get("user_id")
    user_input = message.text
    if not user_input:
        await message.reply("Please provide an answer.")
        return
    is_correct = await check_verb(verb_id, user_input)
    if is_correct:
        await message.reply(
            f"Great! 🎉\nYou fixed your mistake!",
            reply_markup=main_kr(),
        )
        await state.clear()
    else:
        await message.reply(
            "Still incorrect. ❌\nTry again or get a new verb.",
            reply_markup=main_kr(),
        )


@main_router.message(F.text == "Show my score")
async def show_score_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await get_user(tg_user_id=message.from_user.id)
    user_score = await irregular_game_repository.get_user_score_by_id(user.id)
    await message.answer(
        f'Your score in "irregular verbs game": {html.bold((str(user_score.score)))}',
        reply_markup=main_kr(),
    )


async def get_verb_by_id(verb_id: int) -> IrregularVerb:
    verb = await verb_repository.get_irregular_verb_by_id(verb_id)
    return verb


async def check_verb(verb_id: int, user_input: str) -> bool:
    verb = await get_verb_by_id(verb_id)
    if verb is None:
        return False
    user_verbs = [v.strip().lower() for v in user_input.split(" ")]
    if len(user_verbs) != 3:
        logger.info(
            f"User input does not contain exactly 3 verbs. Received: {user_input}"
        )
        return False
    logger.info(f"Checking verb with id={verb_id} against user input: {user_verbs}")

    if (
        verb.base_form.lower() == user_verbs[0]
        and (
            (
                verb.past_simple.lower().split("/")[0].strip() == user_verbs[1]
                or verb.past_simple.lower().split("/")[1].strip() == user_verbs[1]
            )
            if "/" in verb.past_simple
            else verb.past_simple.lower() == user_verbs[1]
        )
        and (
            (
                verb.past_participle.lower().split("/")[0].strip() == user_verbs[2]
                or verb.past_participle.lower().split("/")[1].strip() == user_verbs[2]
            )
            if "/" in verb.past_participle
            else verb.past_participle.lower() == user_verbs[2]
        )
    ):
        logger.info(f"User input matches verb with id={verb_id}. Correct!")
        return True

    logger.info(f"User input does not match verb with id={verb_id}. Incorrect.")
    return False


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
    score = await irregular_game_repository.get_user_score_by_id(user_id)
    return score


async def get_random_verb() -> IrregularVerb:
    verb = await verb_repository.get_random_irregular_verb()
    return verb
