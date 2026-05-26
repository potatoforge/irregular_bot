from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kr() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="Get random verb"),
        ],
        [
            KeyboardButton(text="Show my score"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def i_dont_know_kr() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="I don't know"),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
