import logging
from asyncio import sleep
from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.tg_bot.src.infrastructure.telegram.keyboards.main_keyboard import main_kr
from services.tg_bot.src.container import Container
from services.tg_bot.src.config.settings import settings
from services.tg_bot.src.domain.user import User
from services.tg_bot.src.domain.verb import IrregularVerb

logger = logging.getLogger(__name__)

main_router = Router()

container = Container.build(settings=settings)
user_repository = container.user_repository
verb_repository = container.verb_repository


class VerbStates(StatesGroup):
    waiting_for_verb = State()
    checking_verb = State()


@main_router.message(F.text == "Hello")
@main_router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await set_user(
        tg_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await message.answer("Hello!", reply_markup=main_kr())


@main_router.message(F.text == "Get random verb")
async def cmd_get_random_verb_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    random_verb = await get_random_verb()
    await message.reply(
        f"Random irregular verb:\n"
        f"Base form: {html.bold(html.spoiler(random_verb.base_form))}\n"
        f"Past simple: {html.bold(html.spoiler(random_verb.past_simple))}\n"
        f"Past participle: {html.bold(html.spoiler(random_verb.past_participle))}\n"
        f"Translation: {html.bold(random_verb.translation)}"
    )
    await state.set_state(VerbStates.waiting_for_verb)
    await state.update_data(verb_id=random_verb.id)


@main_router.message(VerbStates.waiting_for_verb)
async def check_verb_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    verb_id = data.get("verb_id")
    if verb_id is None:
        await message.reply("No verb to check. Please get a random verb first.")
        return
    user_input = message.text
    is_correct = await check_verb(verb_id, user_input)
    if is_correct:
        await message.reply("Correct! 🎉", reply_markup=main_kr())
    else:
        verb = await get_verb_by_id(verb_id)
        await message.reply("Incorrect. ❌", reply_markup=main_kr())
        await sleep(0.3)  # Add a small delay before showing the correct answer
        await message.reply(
            f"Random irregular verb:\n"
            f"Base form: {html.bold(verb.base_form)}\n"
            f"Past simple: {html.bold(verb.past_simple)}\n"
            f"Past participle: {html.bold(verb.past_participle)}\n"
            f"Translation: {html.bold(verb.translation)}"
        )
    await state.clear()


async def get_verb_by_id(verb_id: int) -> IrregularVerb:
    verb = await verb_repository.get_irregular_verb_by_id(verb_id)
    return verb


async def check_verb(verb_id: int, user_input: str) -> bool:
    verb = await get_verb_by_id(verb_id)
    if verb is None:
        return False
    user_verbs = [v.strip().lower() for v in user_input.split(" ")]

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
) -> None:
    user = await user_repository.get_user_by_tg_id(tg_user_id)
    if user is None:
        await user_repository.create_user(
            User(
                tg_id=tg_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        )


async def get_random_verb() -> IrregularVerb:
    verb = await verb_repository.get_random_irregular_verb()
    return verb
