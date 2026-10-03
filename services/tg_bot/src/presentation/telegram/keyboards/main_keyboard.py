from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kr() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="Get random verb", style="success"),
        ],
        [
            KeyboardButton(text="Show my score"),
        ],
        [KeyboardButton(text="Get new phrase", style="primary")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def i_dont_know_kr() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="I don't know", style="danger"),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
